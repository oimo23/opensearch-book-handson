#!/usr/bin/env bash
set -euo pipefail

LAB_URL="${LAB_URL:-http://localhost:8100}"

health="$(curl -fsS "${LAB_URL}/api/health")"
jq -e '.status == "ok" and .document_count == 180 and .candidate_size == 10' <<<"${health}" >/dev/null

vector="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"WM-A410でE42が出たときの給水エラーの対処","mode":"vector","top_k":5}')"
jq -e '.hits | length == 5' <<<"${vector}" >/dev/null

fulltext="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"WM-A410でE42が出たときの給水エラーの対処","mode":"fulltext","top_k":5}')"
jq -e '[.hits[].id] | index("error-wm-a410-e42") != null' <<<"${fulltext}" >/dev/null

exact="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"WM-A410-E42","mode":"exact","top_k":3}')"
jq -e '.hits | length == 1 and .[0].id == "error-wm-a410-e42"' <<<"${exact}" >/dev/null

hybrid="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"WM-A410でE42が出たときの給水エラーの対処","mode":"hybrid","top_k":5}')"
jq -e '[.hits[].id] | index("error-wm-a410-e42") != null' <<<"${hybrid}" >/dev/null

filtered="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったもの","mode":"hybrid","filters":{"document_type":"support_case"},"top_k":5}')"
jq -e 'all(.hits[]; .document_type == "support_case")' <<<"${filtered}" >/dev/null
jq -e '[.hits[].id] | index("support-connect-03") != null' <<<"${filtered}" >/dev/null

ranking_query='ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったもの'
ranking_filters='"filters":{"document_type":"support_case"}'
ranking_hybrid="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d "{\"query\":\"${ranking_query}\",\"mode\":\"hybrid\",\"top_k\":10,${ranking_filters}}")"
reranked="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d "{\"query\":\"${ranking_query}\",\"mode\":\"hybrid_rerank\",\"top_k\":10,${ranking_filters}}")"
jq -e '[.hits[].id] | index("support-connect-03") != null' <<<"${ranking_hybrid}" >/dev/null
jq -e '[.hits[].id] | index("support-connect-03") != null' <<<"${reranked}" >/dev/null
jq -e '.total_candidates == 10 and .rerank_ms > 0' <<<"${reranked}" >/dev/null
jq -e --argjson before "$(jq '[.hits[].id] | sort' <<<"${ranking_hybrid}")" \
  '([.hits[].id] | sort) == $before' <<<"${reranked}" >/dev/null

context="$(curl -fsS -X POST "${LAB_URL}/api/search" \
  -H 'Content-Type: application/json' \
  -d '{"query":"WM-A410の無償交換が認められる条件と、対象外になる場合","mode":"hybrid_context","top_k":5}')"
jq -e '[.hits[] | select(.parent_id == "warranty-context-wm-a410")][0].context_chunks | length == 3' <<<"${context}" >/dev/null

echo "appliance support search demo smoke test: passed"
