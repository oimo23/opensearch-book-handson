from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.bootstrap import create_client, current_dataset_sha256, ensure_lab
from app.config import settings
from app.schemas import HealthResponse, SearchRequest, SearchResponse
from app.search import SearchService


STATIC_DIR = Path("/app/static")
client = create_client()
search_service = SearchService(client)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_lab(client)
    yield


app = FastAPI(title="Appliance Support Search Demo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    count = client.count(index=settings.index_name)["count"]
    return HealthResponse(
        status="ok",
        index_name=settings.index_name,
        document_count=count,
        dataset_sha256=current_dataset_sha256(),
        embedding_model=settings.embedding_model_name,
        embedding_model_revision=settings.embedding_model_revision,
        rerank_model=settings.rerank_model_name,
        rerank_model_revision=settings.rerank_model_revision,
        rerank_enabled=settings.enable_rerank,
        candidate_size=settings.candidate_size,
        hybrid_weights=[settings.keyword_weight, settings.vector_weight],
    )


@app.get("/api/documents")
def documents() -> dict:
    response = client.search(
        index=settings.index_name,
        body={
            "size": 500,
            "_source": ["filename", "title"],
            "sort": [{"filename.raw": "asc"}],
            "query": {"match_all": {}},
        },
    )
    items = [hit["_source"] for hit in response["hits"]["hits"]]
    return {"documents": items}


@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    try:
        return search_service.search(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
