#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import platform
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUERIES = ROOT / "data" / "evaluation_queries.json"
EVALUATION_VERSION = "v3"
CATEGORY_MODES = {
    "semantic": ("vector", "fulltext", "hybrid"),
    "lexical": ("vector", "fulltext", "hybrid"),
    "mixed": ("vector", "fulltext", "hybrid"),
    "negation_exception": ("hybrid", "hybrid_rerank"),
    "context": ("hybrid", "hybrid_context"),
}


def hit_matches_filters(hit: dict[str, Any], filters: dict[str, Any]) -> bool:
    if filters.get("document_type") and hit.get("document_type") != filters["document_type"]:
        return False
    if filters.get("product_category") and hit.get("product_category") != filters["product_category"]:
        return False
    if filters.get("firmware_major_gte") is not None:
        version = hit.get("firmware_major")
        if version is None or version < filters["firmware_major_gte"]:
            return False
    if filters.get("device_age_months_gte") is not None:
        age = hit.get("device_age_months")
        if age is None or age < filters["device_age_months_gte"]:
            return False
    if filters.get("support_outcome") and hit.get("support_outcome") != filters["support_outcome"]:
        return False
    return True


def request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 300) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def search(base_url: str, case: dict[str, Any], mode: str) -> dict:
    payload = {
        "query": case["query"],
        "mode": mode,
        "filters": case.get("filters", {}),
        "top_k": 10,
    }
    return request_json(f"{base_url}/api/search", payload)


def reciprocal_rank(hit_ids: list[str], relevance: dict[str, int], k: int = 5) -> float:
    for rank, document_id in enumerate(hit_ids[:k], start=1):
        if relevance.get(document_id, 0) > 0:
            return 1 / rank
    return 0.0


def ndcg(hit_ids: list[str], relevance: dict[str, int], k: int = 5) -> float:
    def dcg(grades: list[int]) -> float:
        return sum((2**grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(grades, 1))

    actual = dcg([relevance.get(document_id, 0) for document_id in hit_ids[:k]])
    ideal = dcg(sorted(relevance.values(), reverse=True)[:k])
    return actual / ideal if ideal else 0.0


def percentile(values: list[int], percent: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, math.ceil(percent * len(ordered)) - 1)
    return ordered[index]


def metric_row(case: dict[str, Any], mode: str, response: dict[str, Any]) -> dict[str, Any]:
    hits = response["hits"]
    hit_ids = [hit["id"] for hit in hits]
    relevance = case.get("relevance", {})
    required = set(case.get("required_context_ids", []))
    restored = {
        chunk["id"]
        for hit in hits
        for chunk in hit.get("context_chunks", [])
    }
    visible_context = set(hit_ids) | restored
    expected = set(case.get("expected_ids", []))
    forbidden = set(case.get("forbidden_ids", []))
    filters = case.get("filters", {})
    filter_violations = (
        sum(not hit_matches_filters(hit, filters) for hit in hits)
        if filters
        else 0
    )
    exact_unexpected = (
        len(set(hit_ids) - expected)
        if mode == "exact" and expected
        else 0
    )
    condition_violations = filter_violations + exact_unexpected
    expected_pass = expected.issubset(set(hit_ids)) if expected else None
    forbidden_violations = len(forbidden & set(hit_ids))
    return {
        "id": case["id"],
        "split": case["split"],
        "category": case["category"],
        "mode": mode,
        "hit_ids": hit_ids,
        "hit_at_3": int(any(document_id in relevance for document_id in hit_ids[:3])),
        "hit_at_10": int(any(document_id in relevance for document_id in hit_ids[:10])),
        "mrr_at_5": reciprocal_rank(hit_ids, relevance),
        "ndcg_at_5": ndcg(hit_ids, relevance),
        "context_completeness": (
            len(required & visible_context) / len(required) if required else None
        ),
        "parent_hit_at_3": (
            int(bool(required & set(hit_ids[:3]))) if required else None
        ),
        "context_precision": (
            len(required & restored) / len(restored) if required and restored else None
        ),
        "context_chunks_added": len(restored - set(hit_ids)) if required else None,
        "expected_pass": expected_pass,
        "condition_violations": condition_violations,
        "forbidden_violations": forbidden_violations,
        "constraint_pass": (
            bool(expected_pass)
            and condition_violations == 0
            and forbidden_violations == 0
            if expected_pass is not None
            else None
        ),
        "timings": {
            key: response[key]
            for key in ("embedding_ms", "search_ms", "rerank_ms", "context_ms", "total_ms")
        },
    }


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["category"], row["mode"])].append(row)
    summary = []
    for (category, mode), items in sorted(groups.items()):
        has_ranking_metrics = category != "constraint"
        summary.append(
            {
                "category": category,
                "mode": mode,
                "queries": len(items),
                "hit_rate_at_3": (
                    sum(item["hit_at_3"] for item in items) / len(items)
                    if has_ranking_metrics else None
                ),
                "hit_rate_at_10": (
                    sum(item["hit_at_10"] for item in items) / len(items)
                    if has_ranking_metrics else None
                ),
                "mrr_at_5": (
                    sum(item["mrr_at_5"] for item in items) / len(items)
                    if has_ranking_metrics else None
                ),
                "ndcg_at_5": (
                    sum(item["ndcg_at_5"] for item in items) / len(items)
                    if has_ranking_metrics else None
                ),
                "context_completeness": (
                    sum(item["context_completeness"] for item in items) / len(items)
                    if items[0]["context_completeness"] is not None
                    else None
                ),
                "parent_hit_rate_at_3": (
                    sum(item["parent_hit_at_3"] for item in items) / len(items)
                    if items[0]["parent_hit_at_3"] is not None
                    else None
                ),
                "context_precision": (
                    sum(
                        item["context_precision"]
                        for item in items
                        if item["context_precision"] is not None
                    )
                    / sum(item["context_precision"] is not None for item in items)
                    if any(item["context_precision"] is not None for item in items)
                    else None
                ),
                "context_chunks_added": (
                    sum(item["context_chunks_added"] for item in items) / len(items)
                    if items[0]["context_chunks_added"] is not None
                    else None
                ),
                "constraint_pass_rate": (
                    sum(bool(item["constraint_pass"]) for item in items) / len(items)
                    if items[0]["constraint_pass"] is not None
                    else None
                ),
                "condition_violations": sum(item["condition_violations"] for item in items),
                "forbidden_violations": sum(item["forbidden_violations"] for item in items),
            }
        )
    return summary


def evaluate_quality(base_url: str, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for case in cases:
        modes = (
            (case["mode"],)
            if case["category"] == "constraint"
            else CATEGORY_MODES[case["category"]]
        )
        for mode in modes:
            rows.append(metric_row(case, mode, search(base_url, case, mode)))
    return rows


def evaluate_latency(
    base_url: str,
    cases: list[dict[str, Any]],
    runs: int,
) -> list[dict[str, Any]]:
    representative: dict[str, tuple[dict[str, Any], str]] = {}
    for case in cases:
        modes = (
            (case["mode"],)
            if case["category"] == "constraint"
            else CATEGORY_MODES[case["category"]]
        )
        for mode in modes:
            representative.setdefault(mode, (case, mode))

    rows = []
    for mode, (case, _) in representative.items():
        search(base_url, case, mode)
        samples: dict[str, list[int]] = defaultdict(list)
        for _ in range(runs):
            response = search(base_url, case, mode)
            for key in ("embedding_ms", "search_ms", "rerank_ms", "context_ms", "total_ms"):
                samples[key].append(response[key])
        rows.append(
            {
                "mode": mode,
                "runs": runs,
                "query_id": case["id"],
                "p50_ms": {key: round(median(values)) for key, values in samples.items()},
                "p95_ms": {key: percentile(values, 0.95) for key, values in samples.items()},
            }
        )
    return rows


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['metadata']['split']} split evaluation",
        "",
        f"- Executed: {result['metadata']['executed_at']}",
        f"- Documents: {result['health']['document_count']}",
        f"- Evaluation version: {result['metadata']['evaluation_version']}",
        f"- Candidate size: {result['health']['candidate_size']}",
        f"- Hybrid weights: {result['health']['hybrid_weights']}",
        "",
        "## Quality by category",
        "",
        "| Category | Mode | Queries | Hit@3 | Hit@10 | MRR@5 | NDCG@5 | Parent@3 | Context | Context precision | Constraint | Violations |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["summary"]:
        hit3 = "-" if row["hit_rate_at_3"] is None else f"{row['hit_rate_at_3']:.3f}"
        hit10 = "-" if row["hit_rate_at_10"] is None else f"{row['hit_rate_at_10']:.3f}"
        mrr = "-" if row["mrr_at_5"] is None else f"{row['mrr_at_5']:.3f}"
        ndcg_value = "-" if row["ndcg_at_5"] is None else f"{row['ndcg_at_5']:.3f}"
        context = "-" if row["context_completeness"] is None else f"{row['context_completeness']:.3f}"
        parent = "-" if row["parent_hit_rate_at_3"] is None else f"{row['parent_hit_rate_at_3']:.3f}"
        precision = "-" if row["context_precision"] is None else f"{row['context_precision']:.3f}"
        constraint = "-" if row["constraint_pass_rate"] is None else f"{row['constraint_pass_rate']:.3f}"
        violations = row["condition_violations"] + row["forbidden_violations"]
        lines.append(
            f"| {row['category']} | `{row['mode']}` | {row['queries']} | "
            f"{hit3} | {hit10} | {mrr} | {ndcg_value} | {parent} | "
            f"{context} | {precision} | {constraint} | {violations} |"
        )
    if result["latency"]:
        lines.extend([
            "",
            "## Latency",
            "",
            "| Mode | Runs | p50 total | p95 total | p50 search | p50 rerank |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for row in result["latency"]:
            lines.append(
                f"| `{row['mode']}` | {row['runs']} | {row['p50_ms']['total_ms']} ms | "
                f"{row['p95_ms']['total_ms']} ms | {row['p50_ms']['search_ms']} ms | "
                f"{row['p50_ms']['rerank_ms']} ms |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8100")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    parser.add_argument("--latency-runs", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    all_cases = json.loads(args.queries.read_text(encoding="utf-8"))
    cases = [case for case in all_cases if case["split"] == args.split]
    base_url = args.base_url.rstrip("/")
    health = request_json(f"{base_url}/api/health")
    quality = evaluate_quality(base_url, cases)
    result = {
        "metadata": {
            "executed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "evaluation_version": EVALUATION_VERSION,
            "split": args.split,
            "host": platform.platform(),
            "python": platform.python_version(),
        },
        "health": health,
        "summary": aggregate(quality),
        "details": quality,
        "latency": (
            evaluate_latency(base_url, cases, args.latency_runs)
            if args.latency_runs > 0
            else []
        ),
    }
    markdown = render_markdown(result)
    print(markdown)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        args.output.with_suffix(".md").write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
