#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from evaluate import request_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "results" / "controlled-examples.json"
EXAMPLES = [
    {
        "id": "strict-article",
        "request": {"query": "第19条", "mode": "vector", "top_k": 3},
    },
    {
        "id": "strict-article-fulltext",
        "request": {"query": "第19条", "mode": "fulltext", "top_k": 3},
    },
    {
        "id": "strict-article-exact",
        "request": {"query": "第19条", "mode": "exact", "top_k": 3},
    },
    {
        "id": "hybrid-rerank-before",
        "request": {"query": "高齢者への勧誘で問題になった事例", "mode": "hybrid", "top_k": 5},
    },
    {
        "id": "hybrid-rerank-after",
        "request": {"query": "高齢者への勧誘で問題になった事例", "mode": "hybrid_rerank", "top_k": 5},
    },
    {
        "id": "context-restoration",
        "request": {
            "query": "高額取引を分割した場合の判定と承認を省略できる例外",
            "mode": "hybrid_context",
            "top_k": 3,
        },
    },
    {
        "id": "structured-filter",
        "request": {
            "query": "複雑な仕組債を販売した事例",
            "mode": "hybrid_filter",
            "top_k": 5,
            "filters": {
                "document_type": "case",
                "customer_age_gte": 75,
                "amount_yen_gte": 5_000_000,
                "case_outcome": "violation",
            },
        },
    },
]


def compact(response: dict) -> dict:
    return {
        "query": response["query"],
        "mode": response["mode"],
        "timings": {
            key: response[key]
            for key in ("embedding_ms", "search_ms", "rerank_ms", "context_ms", "total_ms")
        },
        "total_candidates": response["total_candidates"],
        "request_body": response["request_body"],
        "hits": [
            {
                "rank": hit["rank"],
                "id": hit["id"],
                "title": hit["title"],
                "body": hit["body"],
                "score": hit["score"],
                "rerank_score": hit["rerank_score"],
                "context_chunks": hit["context_chunks"],
            }
            for hit in response["hits"]
        ],
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
        "examples": [
            {
                "id": example["id"],
                "request": example["request"],
                "response": compact(
                    request_json(f"{base_url}/api/search", example["request"])
                ),
            }
            for example in EXAMPLES
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"captured {len(EXAMPLES)} examples to {args.output}")


if __name__ == "__main__":
    main()
