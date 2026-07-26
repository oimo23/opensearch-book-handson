#!/usr/bin/env bash
set -euo pipefail

LAB_URL="${LAB_URL:-http://localhost:8100}"

health="$(curl -fsS "${LAB_URL}/api/health")"
jq -e '.status == "ok" and .document_count == 180 and .candidate_size == 10' <<<"${health}" >/dev/null

vector="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"第19条","mode":"vector","top_k":3}')"
jq -e '.hits | length == 3 and ([.[].id] | index("rule-019") == null)' <<<"${vector}" >/dev/null

fulltext="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"第19条","mode":"fulltext","top_k":3}')"
jq -e '.hits[0].id == "rule-019"' <<<"${fulltext}" >/dev/null

exact="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"第19条","mode":"exact","top_k":3}')"
jq -e '.hits | length == 1 and .[0].id == "rule-019"' <<<"${exact}" >/dev/null

hybrid="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"家族に同席してもらわず、危険性の説明も足りないまま高齢者へ複雑な商品を売ったケース","mode":"hybrid","top_k":5}')"
jq -e '[.hits[].id] | index("elderly-case-01") != null' <<<"${hybrid}" >/dev/null

filtered="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"複雑な仕組債を販売した事例","mode":"hybrid_filter","filters":{"document_type":"case","customer_age_gte":75,"amount_yen_gte":5000000,"case_outcome":"violation"},"top_k":5}')"
jq -e 'all(.hits[]; .document_type == "case" and .customer_age >= 75 and .amount_yen >= 5000000 and .case_outcome == "violation")' <<<"${filtered}" >/dev/null
jq -e '[.hits[].id] | index("elderly-case-01") != null' <<<"${filtered}" >/dev/null

reranked="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"高齢者への勧誘で問題になった事例","mode":"hybrid_rerank","top_k":5}')"
jq -e '.hits[0].id == "elderly-case-01"' <<<"${reranked}" >/dev/null
jq -e '.hits[0].rerank_score > .hits[1].rerank_score' <<<"${reranked}" >/dev/null
jq -e '.total_candidates == 10 and .rerank_ms > 0' <<<"${reranked}" >/dev/null

context="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"高額取引を分割した場合の判定と承認を省略できる例外","mode":"hybrid_context","top_k":5}')"
jq -e '[.hits[] | select(.parent_id == "approval-context-high-value")][0].context_chunks | length == 3' <<<"${context}" >/dev/null

echo "financial document search demo smoke test: passed"
