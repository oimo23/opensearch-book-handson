#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from evaluate import request_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "results" / "controlled-examples.json"
PRODUCT_QUERY = "WM-A410でE42が出たときの給水エラーの対処"
RANKING_QUERY = "ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったもの"
RANKING_FILTERS = {"document_type": "support_case"}
EXAMPLES = [
    {"id": "strict-error-vector", "request": {"query": "WM-A410-E42", "mode": "vector", "top_k": 5}},
    {"id": "strict-error-fulltext", "request": {"query": "WM-A410-E42", "mode": "fulltext", "top_k": 5}},
    {"id": "strict-error-exact", "request": {"query": "WM-A410-E42", "mode": "exact", "top_k": 5}},
    {"id": "product-vector", "request": {"query": PRODUCT_QUERY, "mode": "vector", "top_k": 10}},
    {"id": "product-fulltext", "request": {"query": PRODUCT_QUERY, "mode": "fulltext", "top_k": 10}},
    {"id": "product-hybrid", "request": {"query": PRODUCT_QUERY, "mode": "hybrid", "top_k": 10}},
    {"id": "ranking-hybrid-unfiltered", "request": {"query": RANKING_QUERY, "mode": "hybrid", "top_k": 10}},
    {"id": "ranking-vector", "request": {"query": RANKING_QUERY, "mode": "vector", "top_k": 10, "filters": RANKING_FILTERS}},
    {"id": "ranking-fulltext", "request": {"query": RANKING_QUERY, "mode": "fulltext", "top_k": 10, "filters": RANKING_FILTERS}},
    {"id": "ranking-hybrid", "request": {"query": RANKING_QUERY, "mode": "hybrid", "top_k": 10, "filters": RANKING_FILTERS}},
    {"id": "ranking-rerank", "request": {"query": RANKING_QUERY, "mode": "hybrid_rerank", "top_k": 10, "filters": RANKING_FILTERS}},
    {"id": "context-restoration", "request": {"query": "WM-A410の無償交換が認められる条件と、対象外になる場合", "mode": "hybrid_context", "top_k": 5}},
    {"id": "document-type-filter", "request": {"query": RANKING_QUERY, "mode": "hybrid", "top_k": 5, "filters": RANKING_FILTERS}},
]


def omit_vector_values(value):
    if isinstance(value, dict):
        return {
            key: "[embedding vector omitted]"
            if key == "vector" and isinstance(item, list)
            else omit_vector_values(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [omit_vector_values(item) for item in value]
    return value


def compact(response: dict) -> dict:
    return {
        "query": response["query"], "mode": response["mode"],
        "timings": {key: response[key] for key in ("embedding_ms", "search_ms", "rerank_ms", "context_ms", "total_ms")},
        "total_candidates": response["total_candidates"],
        "request_body": omit_vector_values(response["request_body"]),
        "hits": [{
            "rank": hit["rank"], "id": hit["id"], "title": hit["title"],
            "body": hit["body"], "score": hit["score"],
            "rerank_score": hit["rerank_score"], "context_chunks": hit["context_chunks"],
        } for hit in response["hits"]],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8100")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    output = {
        "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "health": request_json(f"{base_url}/api/health"),
        "examples": [{
            "id": example["id"], "request": example["request"],
            "response": compact(request_json(f"{base_url}/api/search", example["request"])),
        } for example in EXAMPLES],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"captured {len(EXAMPLES)} examples to {args.output}")


if __name__ == "__main__":
    main()
