from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.schemas import SearchFilters, SearchMode, SearchRequest  # noqa: E402
from app.search import build_query  # noqa: E402


class BuildQueryTest(unittest.TestCase):
    def test_exact_uses_term_query(self) -> None:
        request = SearchRequest(query="ALPHA-01", mode=SearchMode.EXACT)
        built = build_query(request, None, 10)
        self.assertEqual(
            built.body["query"],
            {"term": {"identifiers.raw": "ALPHA-01"}},
        )

    def test_hybrid_filter_applies_all_clauses_to_both_queries(self) -> None:
        request = SearchRequest(
            query="複雑な商品の販売事例",
            mode=SearchMode.HYBRID_FILTER,
            filters=SearchFilters(
                document_type="case",
                customer_age_gte=75,
                amount_yen_gte=5_000_000,
                case_outcome="violation",
            ),
        )
        built = build_query(request, [0.0] * 768, 10)
        keyword, vector = built.body["query"]["hybrid"]["queries"]
        expected = [
            {"term": {"document_type": "case"}},
            {"range": {"customer_age": {"gte": 75}}},
            {"range": {"amount_yen": {"gte": 5_000_000}}},
            {"term": {"case_outcome": "violation"}},
        ]
        self.assertEqual(keyword["bool"]["filter"], expected)
        self.assertEqual(
            vector["knn"]["body_vector"]["filter"],
            {"bool": {"filter": expected}},
        )

    def test_hybrid_filter_rejects_empty_filter(self) -> None:
        request = SearchRequest(query="事例", mode=SearchMode.HYBRID_FILTER)
        with self.assertRaisesRegex(ValueError, "structured filter"):
            build_query(request, [0.0] * 768, 10)


if __name__ == "__main__":
    unittest.main()
