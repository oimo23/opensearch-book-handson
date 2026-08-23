#!/usr/bin/env bash
set -euo pipefail

LAB_URL="${LAB_URL:-http://localhost:8100}"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

search() {
  local name="$1"
  local payload="$2"

  curl -fsS --max-time 600 "${LAB_URL}/api/search" \
    -H 'Content-Type: application/json' \
    -d "${payload}" >"${tmp_dir}/${name}.json"
}

assert_ids() {
  local name="$1"
  local expected="$2"

  jq -e --argjson expected "${expected}" \
    '[.hits[].id] == $expected' "${tmp_dir}/${name}.json" >/dev/null
}

echo '[1/6] 起動状態を確認します'
curl -fsS "${LAB_URL}/api/health" >"${tmp_dir}/health.json"
jq -e '.status == "ok" and .document_count == 180 and .candidate_size == 10 and .hybrid_weights == [0.6, 0.4]' \
  "${tmp_dir}/health.json" >/dev/null

echo '[2/6] OMEGA-05の商品説明が返る順位を確認します'
product_query='OMEGA-05で参照指数が下がった場合の元本への影響'
search product-vector "{\"query\":\"${product_query}\",\"mode\":\"vector\",\"top_k\":3}"
search product-fulltext "{\"query\":\"${product_query}\",\"mode\":\"fulltext\",\"top_k\":3}"
search product-hybrid "{\"query\":\"${product_query}\",\"mode\":\"hybrid\",\"top_k\":3}"
assert_ids product-vector '["product-delta-03", "product-omega-50", "product-omega-05"]'
jq -e '.hits[0].id == "product-omega-05"' "${tmp_dir}/product-fulltext.json" >/dev/null
jq -e '.hits[0].id == "product-omega-05"' "${tmp_dir}/product-hybrid.json" >/dev/null

echo '[3/6] 監査問い合わせの候補生成を確認します'
audit_query='高齢者への販売について、後日になって対応の妥当性を裏付けられない事例'
audit_filters='"filters":{"document_type":"case","customer_age_gte":75}'
search audit-vector "{\"query\":\"${audit_query}\",\"mode\":\"vector\",\"top_k\":10,${audit_filters}}"
search audit-fulltext "{\"query\":\"${audit_query}\",\"mode\":\"fulltext\",\"top_k\":10,${audit_filters}}"
search audit-hybrid "{\"query\":\"${audit_query}\",\"mode\":\"hybrid\",\"top_k\":10,${audit_filters}}"
assert_ids audit-vector '["elderly-case-02", "elderly-case-03", "elderly-case-15", "elderly-case-10", "elderly-case-11", "elderly-case-07", "elderly-case-08", "elderly-case-05", "elderly-case-06", "elderly-case-12"]'
assert_ids audit-fulltext '["elderly-case-11", "elderly-case-01", "elderly-case-02", "elderly-case-03", "elderly-case-05", "elderly-case-06", "elderly-case-07", "elderly-case-08", "elderly-case-10", "elderly-case-12"]'
assert_ids audit-hybrid '["elderly-case-11", "elderly-case-02", "elderly-case-03", "elderly-case-15", "elderly-case-10", "elderly-case-07", "elderly-case-08", "elderly-case-05", "elderly-case-06", "elderly-case-12"]'

echo '[4/6] 構造化filterを確認します'
search filtered '{"query":"複雑な仕組債を販売した事例","mode":"hybrid_filter","top_k":5,"filters":{"document_type":"case","customer_age_gte":75,"amount_yen_gte":5000000,"case_outcome":"violation"}}'
jq -e 'all(.hits[]; .document_type == "case" and .customer_age >= 75 and .amount_yen >= 5000000 and .case_outcome == "violation")' \
  "${tmp_dir}/filtered.json" >/dev/null
jq -e '[.hits[0:3][].id] == ["elderly-case-01", "elderly-case-07", "elderly-case-05"]' \
  "${tmp_dir}/filtered.json" >/dev/null

echo '[5/6] filter後の同じ候補をrerankすることを確認します。初回はモデル取得中も画面に進捗が出ません'
search ranking-rerank "{\"query\":\"${audit_query}\",\"mode\":\"hybrid_rerank\",\"top_k\":10,${audit_filters}}"
assert_ids ranking-rerank '["elderly-case-03", "elderly-case-02", "elderly-case-11", "elderly-case-05", "elderly-case-07", "elderly-case-15", "elderly-case-10", "elderly-case-06", "elderly-case-08", "elderly-case-12"]'
jq -e '.hits[0].rerank_score > .hits[1].rerank_score and .total_candidates == 10' \
  "${tmp_dir}/ranking-rerank.json" >/dev/null
jq -e --slurpfile before "${tmp_dir}/audit-hybrid.json" \
  '([.hits[].id] | sort) == ([$before[0].hits[].id] | sort)' \
  "${tmp_dir}/ranking-rerank.json" >/dev/null

echo '[6/6] 前後チャンクの復元を確認します'
search context '{"query":"高齢顧客の継続購入で使える簡易承認の前提と例外","mode":"hybrid_context","top_k":5}'
jq -e '.hits[0].id == "approval-context-elderly-3" and [.hits[0].context_chunks[].id] == ["approval-context-elderly-1", "approval-context-elderly-2", "approval-context-elderly-3"]' \
  "${tmp_dir}/context.json" >/dev/null

echo '第5章の主要な実測結果を再現できました。'
