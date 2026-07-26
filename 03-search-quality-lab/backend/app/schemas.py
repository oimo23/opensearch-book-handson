from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    VECTOR = "vector"
    FULLTEXT = "fulltext"
    EXACT = "exact"
    HYBRID = "hybrid"
    HYBRID_FILTER = "hybrid_filter"
    HYBRID_RERANK = "hybrid_rerank"
    HYBRID_CONTEXT = "hybrid_context"


class SearchFilters(BaseModel):
    document_type: str | None = None
    customer_age_gte: int | None = Field(default=None, ge=0, le=130)
    amount_yen_gte: int | None = Field(default=None, ge=0)
    case_outcome: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    mode: SearchMode = SearchMode.HYBRID
    filename: str | None = None
    filters: SearchFilters = Field(default_factory=SearchFilters)
    top_k: int | None = Field(default=None, ge=1, le=10)


class ContextChunk(BaseModel):
    id: str
    chunk_order: int
    body: str


class SearchHit(BaseModel):
    rank: int
    id: str
    title: str
    filename: str
    category: str
    page_start: int
    body: str
    document_type: str
    customer_age: int | None = None
    amount_yen: int | None = None
    case_outcome: str | None = None
    score: float
    rerank_score: float | None = None
    parent_id: str | None = None
    chunk_order: int | None = None
    context_chunks: list[ContextChunk] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    mode: SearchMode
    took_ms: int
    embedding_ms: int
    search_ms: int
    rerank_ms: int
    context_ms: int
    total_ms: int
    total_candidates: int
    request_body: dict
    hits: list[SearchHit]


class HealthResponse(BaseModel):
    status: str
    index_name: str
    document_count: int
    dataset_sha256: str
    embedding_model: str
    embedding_model_revision: str
    rerank_model: str
    rerank_model_revision: str
    rerank_enabled: bool
    candidate_size: int
    hybrid_weights: list[float]
