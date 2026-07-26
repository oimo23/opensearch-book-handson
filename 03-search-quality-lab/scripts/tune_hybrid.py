#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any
from urllib.request import Request, urlopen

from evaluate import DEFAULT_QUERIES, ndcg, search


WEIGHTS = ((0.3, 0.7), (0.4, 0.6), (0.45, 0.55), (0.5, 0.5), (0.6, 0.4), (0.7, 0.3))


def put_pipeline(opensearch_url: str, pipeline: str, weights: tuple[float, float]) -> None:
    payload: dict[str, Any] = {
        "description": "Dev-tuned keyword and vector score combination",
        "phase_results_processors": [
            {
                "normalization-processor": {
                    "normalization": {"technique": "min_max"},
                    "combination": {
                        "technique": "arithmetic_mean",
                        "parameters": {"weights": list(weights)},
                    },
                }
            }
        ],
    }
    request = Request(
        f"{opensearch_url}/_search/pipeline/{pipeline}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urlopen(request, timeout=30):
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8100")
    parser.add_argument("--opensearch-url", default="http://localhost:9200")
    parser.add_argument("--pipeline", default="fin-doc-hybrid-pipeline")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    args = parser.parse_args()
    cases = [
        case
        for case in json.loads(args.queries.read_text(encoding="utf-8"))
        if case["split"] == "dev"
        and case["category"] in {"semantic", "lexical", "mixed", "negation_exception"}
    ]

    scores = []
    for weights in WEIGHTS:
        put_pipeline(args.opensearch_url.rstrip("/"), args.pipeline, weights)
        category_scores: dict[str, list[float]] = {}
        for case in cases:
            response = search(args.base_url.rstrip("/"), case, "hybrid")
            hit_ids = [hit["id"] for hit in response["hits"]]
            category_scores.setdefault(case["category"], []).append(
                ndcg(hit_ids, case["relevance"])
            )
        macro = mean(mean(values) for values in category_scores.values())
        scores.append((macro, weights))
        print(f"weights={weights} macro_ndcg_at_5={macro:.4f}")

    best_score, best_weights = max(scores, key=lambda item: (item[0], -abs(item[1][0] - 0.5)))
    put_pipeline(args.opensearch_url.rstrip("/"), args.pipeline, best_weights)
    print(f"selected={best_weights} macro_ndcg_at_5={best_score:.4f}")


if __name__ == "__main__":
    main()
