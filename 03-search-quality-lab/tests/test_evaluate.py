from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate import ndcg, reciprocal_rank  # noqa: E402


class EvaluationMetricTest(unittest.TestCase):
    def test_reciprocal_rank_uses_first_relevant_hit(self) -> None:
        self.assertEqual(reciprocal_rank(["x", "target"], {"target": 3}), 0.5)

    def test_ndcg_rewards_better_graded_order(self) -> None:
        relevance = {"best": 3, "acceptable": 1}
        ideal = ndcg(["best", "acceptable"], relevance)
        reversed_order = ndcg(["acceptable", "best"], relevance)
        self.assertEqual(ideal, 1.0)
        self.assertGreater(ideal, reversed_order)


if __name__ == "__main__":
    unittest.main()
