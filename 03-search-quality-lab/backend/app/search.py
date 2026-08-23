from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from opensearchpy import OpenSearch

from app.config import settings
from app.models import models
from app.schemas import ContextChunk, SearchHit, SearchMode, SearchRequest, SearchResponse


@dataclass(frozen=True)
class BuiltQuery:
    body: dict[str, Any]
    pipeline: str | None = None


def _filter_clauses(request: SearchRequest) -> list[dict[str, Any]]:
    clauses: list[dict[str, Any]] = []
    if request.filename:
        clauses.append({"term": {"filename.raw": request.filename}})
    if request.filters.document_type:
        clauses.append({"term": {"document_type": request.filters.document_type}})
    if request.filters.customer_age_gte is not None:
        clauses.append({"range": {"customer_age": {"gte": request.filters.customer_age_gte}}})
    if request.filters.amount_yen_gte is not None:
        clauses.append({"range": {"amount_yen": {"gte": request.filters.amount_yen_gte}}})
    if request.filters.case_outcome:
        clauses.append({"term": {"case_outcome": request.filters.case_outcome}})
    return clauses


def _combined_filter(clauses: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"bool": {"filter": clauses}}


def build_query(
    request: SearchRequest,
    query_vector: list[float] | None,
    candidate_size: int,
) -> BuiltQuery:
    source_fields = [
        "id",
        "family",
        "title",
        "filename",
        "category",
        "page_start",
        "body",
        "parent_id",
        "chunk_order",
        "document_type",
        "customer_age",
        "amount_yen",
        "case_outcome",
    ]
    filter_clauses = _filter_clauses(request)
    filter_clause = _combined_filter(filter_clauses)

    if request.mode is SearchMode.VECTOR:
        if query_vector is None:
            raise ValueError("vector mode requires a query vector")
        vector_query: dict[str, Any] = {"vector": query_vector, "k": candidate_size}
        if filter_clause:
            vector_query["filter"] = filter_clause
        return BuiltQuery(
            body={
                "size": candidate_size,
                "_source": source_fields,
                "query": {"knn": {"body_vector": vector_query}},
            }
        )

    if request.mode is SearchMode.FULLTEXT:
        match_query: dict[str, Any] = {
            "multi_match": {
                "query": request.query,
                "fields": ["title^2", "body", "identifiers^3"],
                "type": "best_fields",
            }
        }
        query = (
            {"bool": {"must": [match_query], "filter": filter_clauses}}
            if filter_clauses
            else match_query
        )
        return BuiltQuery(body={"size": candidate_size, "_source": source_fields, "query": query})

    if request.mode is SearchMode.EXACT:
        return BuiltQuery(
            body={
                "size": candidate_size,
                "_source": source_fields,
                "query": {"term": {"identifiers.raw": request.query}},
            }
        )

    if query_vector is None:
        raise ValueError(f"{request.mode.value} mode requires a query vector")

    keyword_query: dict[str, Any] = {
        "multi_match": {
            "query": request.query,
            "fields": ["title^2", "body", "identifiers^3"],
            "type": "best_fields",
        }
    }
    vector_options: dict[str, Any] = {"vector": query_vector, "k": candidate_size}
    if request.mode is SearchMode.HYBRID_FILTER and not filter_clauses:
        raise ValueError("hybrid_filter requires at least one structured filter")
    if filter_clauses:
        keyword_query = {"bool": {"must": [keyword_query], "filter": filter_clauses}}
        vector_options["filter"] = filter_clause

    return BuiltQuery(
        body={
            "size": candidate_size,
            "_source": source_fields,
            "query": {
                "hybrid": {
                    "queries": [
                        keyword_query,
                        {"knn": {"body_vector": vector_options}},
                    ]
                }
            },
        },
        pipeline=settings.pipeline_name,
    )


class SearchService:
    def __init__(self, client: OpenSearch):
        self.client = client

    def search(self, request: SearchRequest) -> SearchResponse:
        total_started = perf_counter()
        top_k = request.top_k or settings.top_k
        candidate_size = max(settings.candidate_size, top_k)
        needs_vector = request.mode not in {SearchMode.FULLTEXT, SearchMode.EXACT}
        embedding_started = perf_counter()
        query_vector = models.embed_query(request.query) if needs_vector else None
        embedding_ms = round((perf_counter() - embedding_started) * 1000)
        built = build_query(request, query_vector, candidate_size)

        params = {"search_pipeline": built.pipeline} if built.pipeline else None
        search_started = perf_counter()
        raw = self.client.search(index=settings.index_name, body=built.body, params=params)
        search_ms = round((perf_counter() - search_started) * 1000)
        raw_hits = raw.get("hits", {}).get("hits", [])
        total_candidates = len(raw_hits)

        rerank_scores: dict[str, float] = {}
        rerank_ms = 0
        if request.mode is SearchMode.HYBRID_RERANK and raw_hits:
            rerank_started = perf_counter()
            documents = [
                f"{hit['_source']['title']}\n{hit['_source']['body']}"
                for hit in raw_hits
            ]
            scores = models.rerank(request.query, documents)
            rerank_scores = {hit["_id"]: score for hit, score in zip(raw_hits, scores, strict=True)}
            raw_hits = sorted(raw_hits, key=lambda hit: rerank_scores[hit["_id"]], reverse=True)
            rerank_ms = round((perf_counter() - rerank_started) * 1000)

        context_chunks: dict[str, list[ContextChunk]] = {}
        context_ms = 0
        if request.mode is SearchMode.HYBRID_CONTEXT:
            context_started = perf_counter()
            unique_hits = []
            seen_groups: set[str] = set()
            for hit in raw_hits:
                group = hit["_source"].get("parent_id") or hit["_id"]
                if group not in seen_groups:
                    unique_hits.append(hit)
                    seen_groups.add(group)
            raw_hits = unique_hits
            for hit in raw_hits[:top_k]:
                parent_id = hit["_source"].get("parent_id")
                if parent_id and parent_id not in context_chunks:
                    context_chunks[parent_id] = self._load_context_chunks(parent_id)
            context_ms = round((perf_counter() - context_started) * 1000)

        hits: list[SearchHit] = []
        for rank, hit in enumerate(raw_hits[:top_k], start=1):
            source = hit["_source"]
            hits.append(
                SearchHit(
                    rank=rank,
                    id=source["id"],
                    title=source["title"],
                    filename=source["filename"],
                    category=source["category"],
                    page_start=source["page_start"],
                    body=source["body"],
                    document_type=source["document_type"],
                    customer_age=source.get("customer_age"),
                    amount_yen=source.get("amount_yen"),
                    case_outcome=source.get("case_outcome"),
                    score=float(hit.get("_score") or 0.0),
                    rerank_score=rerank_scores.get(hit["_id"]),
                    parent_id=source.get("parent_id"),
                    chunk_order=source.get("chunk_order"),
                    context_chunks=context_chunks.get(source.get("parent_id"), []),
                )
            )

        total_ms = round((perf_counter() - total_started) * 1000)
        return SearchResponse(
            query=request.query,
            mode=request.mode,
            took_ms=total_ms,
            embedding_ms=embedding_ms,
            search_ms=search_ms,
            rerank_ms=rerank_ms,
            context_ms=context_ms,
            total_ms=total_ms,
            total_candidates=total_candidates,
            request_body=built.body,
            hits=hits,
        )

    def _load_context_chunks(self, parent_id: str) -> list[ContextChunk]:
        response = self.client.search(
            index=settings.index_name,
            body={
                "size": 20,
                "_source": ["id", "chunk_order", "body"],
                "sort": [{"chunk_order": "asc"}],
                "query": {"term": {"parent_id": parent_id}},
            },
        )
        return [
            ContextChunk(
                id=hit["_source"]["id"],
                chunk_order=hit["_source"]["chunk_order"],
                body=hit["_source"]["body"],
            )
            for hit in response["hits"]["hits"]
        ]
