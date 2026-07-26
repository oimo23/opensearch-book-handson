from __future__ import annotations

from threading import Lock

import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

from app.config import settings


class ModelRegistry:
    def __init__(self) -> None:
        self._embedder: SentenceTransformer | None = None
        self._reranker: CrossEncoder | None = None
        self._lock = Lock()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        prepared = [f"検索文書: {text.strip()}" for text in texts]
        return self._encode(prepared)

    def embed_query(self, text: str) -> list[float]:
        return self._encode([f"検索クエリ: {text.strip()}"])[0]

    def rerank(self, query: str, documents: list[str]) -> list[float]:
        if not settings.enable_rerank:
            raise RuntimeError("rerank is disabled by ENABLE_RERANK")
        pairs = [(query, document) for document in documents]
        scores = self._reranker_instance().predict(pairs, show_progress_bar=False)
        return np.asarray(scores, dtype=np.float32).reshape(-1).tolist()

    def _encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self._embedder_instance().encode(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32).tolist()

    def _embedder_instance(self) -> SentenceTransformer:
        if self._embedder is None:
            with self._lock:
                if self._embedder is None:
                    self._embedder = SentenceTransformer(
                        settings.embedding_model_name,
                        revision=settings.embedding_model_revision,
                    )
        return self._embedder

    def _reranker_instance(self) -> CrossEncoder:
        if self._reranker is None:
            with self._lock:
                if self._reranker is None:
                    self._reranker = CrossEncoder(
                        settings.rerank_model_name,
                        revision=settings.rerank_model_revision,
                        max_length=512,
                    )
        return self._reranker


models = ModelRegistry()
