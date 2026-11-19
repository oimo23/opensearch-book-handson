from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.schemas import SearchFilters, SearchMode, SearchRequest  # noqa: E402
from app.search import _identifier_terms, build_query  # noqa: E402


class BuildQueryTest(unittest.TestCase):
    def test_extracts_identifiers_from_natural_language(self) -> None:
        self.assertEqual(
            _identifier_terms("WM-A410でE42が出たときの対処"),
            ["WM-A410", "E42"],
        )

    def test_fulltext_adds_exact_identifier_terms(self) -> None:
        request = SearchRequest(
            query="WM-A410でE42が出たときの対処",
            mode=SearchMode.FULLTEXT,
        )
        built = build_query(request, None, 10)
        should = built.body["query"]["bool"]["should"]
        self.assertEqual(
            should[1:],
            [
                {"term": {"identifiers.raw": {"value": "WM-A410", "boost": 3}}},
                {"term": {"identifiers.raw": {"value": "E42", "boost": 3}}},
            ],
        )

    def test_exact_uses_term_query(self) -> None:
        request = SearchRequest(query="WM-A410-E42", mode=SearchMode.EXACT)
        built = build_query(request, None, 10)
        self.assertEqual(
            built.body["query"],
            {"term": {"identifiers.raw": "WM-A410-E42"}},
        )

    def test_hybrid_applies_document_type_to_both_queries(self) -> None:
        request = SearchRequest(
            query="更新後も接続できない洗濯機の事例",
            mode=SearchMode.HYBRID,
            filters=SearchFilters(document_type="support_case"),
        )
        built = build_query(request, [0.0] * 768, 10)
        keyword, vector = built.body["query"]["hybrid"]["queries"]
        expected = [{"term": {"document_type": "support_case"}}]
        self.assertEqual(keyword["bool"]["filter"], expected)
        self.assertEqual(
            vector["knn"]["body_vector"]["filter"],
            expected[0],
        )

    def test_hybrid_allows_search_without_filter(self) -> None:
        request = SearchRequest(query="事例", mode=SearchMode.HYBRID)
        built = build_query(request, [0.0] * 768, 10)
        keyword, vector = built.body["query"]["hybrid"]["queries"]
        self.assertIn("bool", keyword)
        self.assertNotIn("filter", vector["knn"]["body_vector"])

    def test_hybrid_rerank_applies_filters_before_reranking(self) -> None:
        request = SearchRequest(
            query="更新後も接続できない事例",
            mode=SearchMode.HYBRID_RERANK,
            filters=SearchFilters(document_type="support_case"),
        )
        built = build_query(request, [0.0] * 768, 10)
        keyword, vector = built.body["query"]["hybrid"]["queries"]
        expected = [{"term": {"document_type": "support_case"}}]
        self.assertEqual(keyword["bool"]["filter"], expected)
        self.assertEqual(
            vector["knn"]["body_vector"]["filter"],
            expected[0],
        )


if __name__ == "__main__":
    unittest.main()
