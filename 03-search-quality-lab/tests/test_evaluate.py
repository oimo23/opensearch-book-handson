from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate import aggregate, hit_matches_filters, metric_row, ndcg, reciprocal_rank  # noqa: E402


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
            "document_type": "support_case",
            "product_category": "washer",
            "firmware_major_gte": 3,
            "device_age_months_gte": 12,
            "support_outcome": "unresolved",
        }
        matching = {
            "document_type": "support_case",
            "product_category": "washer",
            "firmware_major": 4,
            "device_age_months": 18,
            "support_outcome": "unresolved",
        }
        self.assertTrue(hit_matches_filters(matching, filters))
        self.assertFalse(hit_matches_filters({**matching, "firmware_major": 2}, filters))

    def test_constraint_summary_omits_ranking_metrics(self) -> None:
        row = {
            "category": "constraint",
            "mode": "exact",
            "hit_at_3": 0,
            "hit_at_10": 0,
            "mrr_at_5": 0.0,
            "ndcg_at_5": 0.0,
            "context_completeness": None,
            "parent_hit_at_3": None,
            "context_precision": None,
            "context_chunks_added": None,
            "constraint_pass": True,
            "condition_violations": 0,
            "forbidden_violations": 0,
        }
        summary = aggregate([row])[0]
        self.assertIsNone(summary["hit_rate_at_3"])
        self.assertIsNone(summary["ndcg_at_5"])
        self.assertEqual(summary["constraint_pass_rate"], 1.0)

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
