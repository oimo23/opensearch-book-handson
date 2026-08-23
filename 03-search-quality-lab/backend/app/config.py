from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    opensearch_url: str = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    index_name: str = os.getenv("OPENSEARCH_INDEX", "appliance-support-demo-v1")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "cl-nagoya/ruri-v3-310m")
    embedding_model_revision: str = os.getenv(
        "EMBEDDING_MODEL_REVISION",
        "18b60fb8c2b9df296fb4212bb7d23ef94e579cd3",
    )
    rerank_model_name: str = os.getenv("RERANK_MODEL_NAME", "BAAI/bge-reranker-v2-m3")
    rerank_model_revision: str = os.getenv(
        "RERANK_MODEL_REVISION",
        "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e",
    )
    enable_rerank: bool = os.getenv("ENABLE_RERANK", "true").lower() in {"1", "true", "yes"}
    top_k: int = int(os.getenv("TOP_K", "5"))
    candidate_size: int = int(os.getenv("CANDIDATE_SIZE", "10"))
    keyword_weight: float = float(os.getenv("HYBRID_KEYWORD_WEIGHT", "0.7"))
    vector_weight: float = float(os.getenv("HYBRID_VECTOR_WEIGHT", "0.3"))
    embedding_dimensions: int = 768
    pipeline_name: str = "appliance-hybrid"


settings = Settings()
