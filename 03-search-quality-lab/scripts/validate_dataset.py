#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "corpus.jsonl"
QUERIES_PATH = ROOT / "data" / "evaluation_queries.json"
REQUIRED_DOCUMENT_FIELDS = {
    "id", "family", "title", "filename", "category", "page_start", "identifiers",
    "parent_id", "chunk_order", "document_type", "customer_age", "amount_yen",
    "case_outcome", "synthetic", "body",
}
EXPECTED_QUERY_COUNTS = {
    ("dev", "semantic"): 5,
    ("test", "semantic"): 5,
    ("dev", "lexical"): 5,
    ("test", "lexical"): 5,
    ("dev", "mixed"): 5,
    ("test", "mixed"): 5,
    ("dev", "negation_exception"): 5,
    ("test", "negation_exception"): 5,
    ("dev", "context"): 3,
    ("test", "context"): 3,
    ("dev", "constraint"): 2,
    ("test", "constraint"): 2,
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate() -> None:
    documents = load_jsonl(CORPUS_PATH)
    queries = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    document_ids = [row.get("id") for row in documents]
    document_id_set = set(document_ids)

    if len(documents) != 180:
        errors.append(f"corpus must contain 180 chunks, got {len(documents)}")
    if len(document_id_set) != len(document_ids):
        errors.append("document ids must be unique")
    if len(queries) != 50:
        errors.append(f"evaluation set must contain 50 queries, got {len(queries)}")

    for row in documents:
        missing = REQUIRED_DOCUMENT_FIELDS - row.keys()
        if missing:
            errors.append(f"{row.get('id')}: missing fields {sorted(missing)}")
        if not row.get("synthetic"):
            errors.append(f"{row.get('id')}: synthetic must be true")
        if not row.get("body"):
            errors.append(f"{row.get('id')}: body must not be empty")

    parent_orders: dict[str, list[int]] = defaultdict(list)
    for row in documents:
        if row.get("parent_id"):
            if row.get("chunk_order") is None:
                errors.append(f"{row['id']}: parent chunk requires chunk_order")
            else:
                parent_orders[row["parent_id"]].append(row["chunk_order"])
        elif row.get("chunk_order") is not None:
            errors.append(f"{row['id']}: chunk_order requires parent_id")
    for parent_id, orders in parent_orders.items():
        expected = list(range(1, len(orders) + 1))
        if sorted(orders) != expected:
            errors.append(f"{parent_id}: chunk_order must be contiguous, got {sorted(orders)}")

    query_ids = [row.get("id") for row in queries]
    if len(set(query_ids)) != len(query_ids):
        errors.append("query ids must be unique")
    counts = Counter((row.get("split"), row.get("category")) for row in queries)
    if counts != Counter(EXPECTED_QUERY_COUNTS):
        errors.append(f"unexpected split/category counts: {dict(counts)}")

    groups_by_split: dict[str, set[str]] = defaultdict(set)
    for row in queries:
        groups_by_split[row["split"]].add(row["case_group"])
        referenced = (
            set(row.get("relevance", {}))
            | set(row.get("required_context_ids", []))
            | set(row.get("expected_ids", []))
            | set(row.get("forbidden_ids", []))
        )
        unknown = referenced - document_id_set
        if unknown:
            errors.append(f"{row['id']}: unknown document ids {sorted(unknown)}")
        required = row.get("required_context_ids", [])
        if required:
            parents = {
                next(doc["parent_id"] for doc in documents if doc["id"] == document_id)
                for document_id in required
            }
            if len(parents) != 1 or None in parents:
                errors.append(f"{row['id']}: required context must share one parent")

    overlap = groups_by_split["dev"] & groups_by_split["test"]
    if overlap:
        errors.append(f"case groups must not cross dev/test: {sorted(overlap)}")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print(
        f"dataset valid: {len(documents)} chunks, {len(parent_orders)} parents, "
        f"{len(queries)} queries"
    )


if __name__ == "__main__":
    validate()
