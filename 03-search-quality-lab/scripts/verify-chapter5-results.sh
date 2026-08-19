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

echo '[1/7] 起動状態を確認します'
curl -fsS "${LAB_URL}/api/health" >"${tmp_dir}/health.json"
jq -e '.status == "ok" and .document_count == 180 and .candidate_size == 10 and .hybrid_weights == [0.6, 0.4]' \
  "${tmp_dir}/health.json" >/dev/null

echo '[2/7] 第19条のvector、全文検索、完全一致を確認します'
search article-vector '{"query":"第19条","mode":"vector","top_k":10}'
search article-fulltext '{"query":"第19条","mode":"fulltext","top_k":3}'
search article-exact '{"query":"第19条","mode":"exact","top_k":3}'
jq -e '.hits | length == 10 and ([.[].id] | index("rule-019") == null)' \
  "${tmp_dir}/article-vector.json" >/dev/null
assert_ids article-fulltext '["rule-019", "rule-019-2"]'
assert_ids article-exact '["rule-019"]'

echo '[3/7] 問い合わせ表現による順位差を確認します'
semantic_query='説明した証拠が残っておらず、後から適切だったか確かめられない高齢者販売'
search semantic-vector "{\"query\":\"${semantic_query}\",\"mode\":\"vector\",\"top_k\":10}"
search semantic-fulltext "{\"query\":\"${semantic_query}\",\"mode\":\"fulltext\",\"top_k\":10}"
search semantic-hybrid "{\"query\":\"${semantic_query}\",\"mode\":\"hybrid\",\"top_k\":10}"
jq -e '[.hits[].id] | index("elderly-case-03") == 0' "${tmp_dir}/semantic-vector.json" >/dev/null
jq -e '[.hits[].id] | index("elderly-case-03") == 7' "${tmp_dir}/semantic-fulltext.json" >/dev/null
jq -e '[.hits[].id] | index("elderly-case-03") == 1' "${tmp_dir}/semantic-hybrid.json" >/dev/null

search identifier-vector '{"query":"CASE-ELDERLY-03","mode":"vector","top_k":10}'
search identifier-fulltext '{"query":"CASE-ELDERLY-03","mode":"fulltext","top_k":10}'
search identifier-hybrid '{"query":"CASE-ELDERLY-03","mode":"hybrid","top_k":10}'
jq -e '[.hits[].id] | index("elderly-case-03") == null' "${tmp_dir}/identifier-vector.json" >/dev/null
jq -e '[.hits[].id] | index("elderly-case-03") == 0' "${tmp_dir}/identifier-fulltext.json" >/dev/null
jq -e '[.hits[].id] | index("elderly-case-03") == 0' "${tmp_dir}/identifier-hybrid.json" >/dev/null

echo '[4/7] 監査問い合わせの候補生成を確認します'
audit_query='高齢顧客への複雑な金融商品の販売で、説明不足と管理者承認の欠落が問題になった事例'
search audit-vector "{\"query\":\"${audit_query}\",\"mode\":\"vector\",\"top_k\":3}"
search audit-fulltext "{\"query\":\"${audit_query}\",\"mode\":\"fulltext\",\"top_k\":3}"
search audit-hybrid "{\"query\":\"${audit_query}\",\"mode\":\"hybrid\",\"top_k\":3}"
assert_ids audit-vector '["elderly-case-01", "rule-019", "elderly-case-04"]'
assert_ids audit-fulltext '["rule-019", "approval-context-elderly-1", "elderly-case-15"]'
assert_ids audit-hybrid '["rule-019", "elderly-case-01", "approval-context-elderly-1"]'

echo '[5/7] 構造化filterを確認します'
search filtered '{"query":"複雑な仕組債を販売した事例","mode":"hybrid_filter","top_k":5,"filters":{"document_type":"case","customer_age_gte":75,"amount_yen_gte":5000000,"case_outcome":"violation"}}'
jq -e 'all(.hits[]; .document_type == "case" and .customer_age >= 75 and .amount_yen >= 5000000 and .case_outcome == "violation")' \
  "${tmp_dir}/filtered.json" >/dev/null
jq -e '[.hits[0:3][].id] == ["elderly-case-01", "elderly-case-07", "elderly-case-05"]' \
  "${tmp_dir}/filtered.json" >/dev/null

echo '[6/7] rerankを確認します。初回はモデル取得中も画面に進捗が出ません'
search audit-rerank "{\"query\":\"${audit_query}\",\"mode\":\"hybrid_rerank\",\"top_k\":3}"
assert_ids audit-rerank '["elderly-case-01", "elderly-case-04", "elderly-case-15"]'
jq -e '.hits[0].rerank_score > .hits[1].rerank_score and .total_candidates == 10' \
  "${tmp_dir}/audit-rerank.json" >/dev/null

echo '[7/7] 前後チャンクの復元を確認します'
search context '{"query":"高齢顧客の継続購入で使える簡易承認の前提と例外","mode":"hybrid_context","top_k":5}'
jq -e '.hits[0].id == "approval-context-elderly-3" and [.hits[0].context_chunks[].id] == ["approval-context-elderly-1", "approval-context-elderly-2", "approval-context-elderly-3"]' \
  "${tmp_dir}/context.json" >/dev/null

echo '第5章の主要な実測結果を再現できました。'
