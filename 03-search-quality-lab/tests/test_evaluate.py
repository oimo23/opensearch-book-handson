from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate import hit_matches_filters, metric_row, ndcg, reciprocal_rank  # noqa: E402


class EvaluationMetricTest(unittest.TestCase):
    def test_reciprocal_rank_uses_first_relevant_hit(self) -> None:
        self.assertEqual(reciprocal_rank(["x", "target"], {"target": 3}), 0.5)

    def test_ndcg_rewards_better_graded_order(self) -> None:
        relevance = {"best": 3, "acceptable": 1}
        ideal = ndcg(["best", "acceptable"], relevance)
        reversed_order = ndcg(["acceptable", "best"], relevance)
        self.assertEqual(ideal, 1.0)
        self.assertGreater(ideal, reversed_order)

    def test_filter_validation_checks_returned_fields(self) -> None:
        filters = {
            "document_type": "case",
            "customer_age_gte": 75,
            "amount_yen_gte": 5_000_000,
            "case_outcome": "violation",
        }
        matching = {
            "document_type": "case",
            "customer_age": 78,
            "amount_yen": 5_000_000,
            "case_outcome": "violation",
        }
        self.assertTrue(hit_matches_filters(matching, filters))
        self.assertFalse(hit_matches_filters({**matching, "customer_age": 74}, filters))

    def test_context_metrics_separate_parent_hit_and_expansion_precision(self) -> None:
        case = {
            "id": "ctx",
            "split": "test",
            "category": "context",
            "relevance": {"parent-1": 1, "parent-2": 1, "parent-3": 3},
            "required_context_ids": ["parent-1", "parent-2", "parent-3"],
        }
        response = {
            "hits": [
                {
                    "id": "parent-1",
                    "context_chunks": [
                        {"id": "parent-1"},
                        {"id": "parent-2"},
                        {"id": "parent-3"},
                        {"id": "other-parent-1"},
                    ],
                }
            ],
            "embedding_ms": 1,
            "search_ms": 1,
            "rerank_ms": 0,
            "context_ms": 1,
            "total_ms": 3,
        }
        row = metric_row(case, "hybrid_context", response)
        self.assertEqual(row["parent_hit_at_3"], 1)
        self.assertEqual(row["context_completeness"], 1.0)
        self.assertEqual(row["context_precision"], 0.75)
        self.assertEqual(row["context_chunks_added"], 3)


if __name__ == "__main__":
    unittest.main()
