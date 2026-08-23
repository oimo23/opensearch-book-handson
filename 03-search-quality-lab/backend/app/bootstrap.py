from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from opensearchpy import OpenSearch, helpers

from app.config import settings
from app.models import models


CORPUS_PATH = Path("/app/data/corpus.jsonl")


def create_client() -> OpenSearch:
    return OpenSearch(settings.opensearch_url, use_ssl=False, verify_certs=False, timeout=120)


def ensure_lab(client: OpenSearch) -> None:
    _ensure_pipeline(client)
    documents = _load_corpus()
    dataset_sha256 = current_dataset_sha256()
    if client.indices.exists(index=settings.index_name):
        mapping = client.indices.get_mapping(index=settings.index_name)
        indexed_hash = (
            mapping.get(settings.index_name, {})
            .get("mappings", {})
            .get("_meta", {})
            .get("dataset_sha256")
        )
        indexed_count = client.count(index=settings.index_name)["count"]
        if indexed_hash == dataset_sha256 and indexed_count == len(documents):
            return
        client.indices.delete(index=settings.index_name)
    client.indices.create(
        index=settings.index_name,
        body=_index_definition(dataset_sha256),
    )
    vectors = models.embed_documents([_embedding_text(document) for document in documents])
    actions = [
        {
            "_op_type": "index",
            "_index": settings.index_name,
            "_id": document["id"],
            "_source": {**document, "body_vector": vector},
        }
        for document, vector in zip(documents, vectors, strict=True)
    ]
    helpers.bulk(client, actions, refresh="wait_for")


def _ensure_pipeline(client: OpenSearch) -> None:
    if round(settings.keyword_weight + settings.vector_weight, 6) != 1.0:
        raise ValueError("hybrid weights must add up to 1.0")
    client.transport.perform_request(
        "PUT",
        f"/_search/pipeline/{settings.pipeline_name}",
        body={
            "description": "Normalize and combine keyword and vector scores for the appliance support search demo",
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {
                                "weights": [settings.keyword_weight, settings.vector_weight]
                            },
                        },
                    }
                }
            ],
        },
    )


def _index_definition(dataset_sha256: str) -> dict[str, Any]:
    return {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "_meta": {"dataset_sha256": dataset_sha256},
            "properties": {
                "id": {"type": "keyword"},
                "family": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "cjk"},
                "filename": {
                    "type": "text",
                    "analyzer": "cjk",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "category": {"type": "keyword"},
                "page_start": {"type": "integer"},
                "document_type": {"type": "keyword"},
                "product_category": {"type": "keyword"},
                "firmware_major": {"type": "integer"},
                "device_age_months": {"type": "integer"},
                "support_outcome": {"type": "keyword"},
                "synthetic": {"type": "boolean"},
                "identifiers": {
                    "type": "text",
                    "analyzer": "whitespace",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "parent_id": {"type": "keyword"},
                "chunk_order": {"type": "integer"},
                "body": {"type": "text", "analyzer": "cjk"},
                "body_vector": {
                    "type": "knn_vector",
                    "dimension": settings.embedding_dimensions,
                    "method": {
                        "name": "hnsw",
                        "engine": "lucene",
                        "space_type": "cosinesimil",
                    },
                },
            }
        },
    }


def _load_corpus() -> list[dict[str, Any]]:
    with CORPUS_PATH.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def current_dataset_sha256() -> str:
    return sha256(CORPUS_PATH.read_bytes()).hexdigest()


def _embedding_text(document: dict[str, Any]) -> str:
    return f"{document['title']}\n{document['body']}"
