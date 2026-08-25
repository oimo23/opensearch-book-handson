#!/usr/bin/env bash
set -euo pipefail

LAB_URL="${LAB_URL:-http://localhost:8100}"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

search() {
  local name="$1"
  local payload="$2"
  curl -fsS --max-time 600 "${LAB_URL}/api/search" \
    -H 'Content-Type: application/json' -d "${payload}" >"${tmp_dir}/${name}.json"
}

echo '[1/5] 起動状態を確認します'
curl -fsS "${LAB_URL}/api/health" >"${tmp_dir}/health.json"
jq -e '.status == "ok" and .index_name == "appliance-support-demo-v1" and .document_count == 180 and .candidate_size == 10 and .hybrid_weights == [0.7, 0.3]' "${tmp_dir}/health.json" >/dev/null

echo '[2/5] WM-A410 / E42の候補生成を確認します'
product_query='WM-A410でE42が出たときの給水エラーの対処'
for mode in vector fulltext hybrid; do
  search "product-${mode}" "{\"query\":\"${product_query}\",\"mode\":\"${mode}\",\"top_k\":10}"
  jq -e '[.hits[].id] | index("error-wm-a410-e42") != null' "${tmp_dir}/product-${mode}.json" >/dev/null
done
jq -e '.hits[0].id == "repair-case-11" and .hits[1].id == "error-wm-a410-e42"' "${tmp_dir}/product-vector.json" >/dev/null
jq -e '.hits[0].id == "error-wm-a410-e42"' "${tmp_dir}/product-fulltext.json" >/dev/null
jq -e '.hits[0].id == "error-wm-a410-e42"' "${tmp_dir}/product-hybrid.json" >/dev/null

echo '[3/5] 同じ10件をrerankすることを確認します'
ranking_query='ファームウェア3以降で、ソフトウェアを更新した後、再登録や再起動を試しても接続できなかったもの'
ranking_filters='"filters":{"document_type":"support_case"}'
search ranking-unfiltered "{\"query\":\"${ranking_query}\",\"mode\":\"hybrid\",\"top_k\":10}"
search ranking-hybrid "{\"query\":\"${ranking_query}\",\"mode\":\"hybrid\",\"top_k\":10,${ranking_filters}}"
search ranking-rerank "{\"query\":\"${ranking_query}\",\"mode\":\"hybrid_rerank\",\"top_k\":10,${ranking_filters}}"
jq -e '[.hits[].document_type] | index("release_note") != null' "${tmp_dir}/ranking-unfiltered.json" >/dev/null
jq -e 'all(.hits[]; .document_type == "support_case")' "${tmp_dir}/ranking-hybrid.json" >/dev/null
jq -e '[.hits[].id] | index("support-connect-03") != null' "${tmp_dir}/ranking-hybrid.json" >/dev/null
jq -e '[.hits[].id] | index("support-connect-03") != null' "${tmp_dir}/ranking-rerank.json" >/dev/null
jq -e --slurpfile before "${tmp_dir}/ranking-hybrid.json" '([.hits[].id] | sort) == ([$before[0].hits[].id] | sort)' "${tmp_dir}/ranking-rerank.json" >/dev/null
jq -e '.hits[0].id == "support-connect-13" and .hits[1].id == "support-connect-03" and .hits[2].id == "support-connect-01"' "${tmp_dir}/ranking-hybrid.json" >/dev/null
jq -e '.hits[0].id == "support-connect-03" and .hits[1].id == "support-connect-13" and .hits[2].id == "support-connect-01"' "${tmp_dir}/ranking-rerank.json" >/dev/null

echo '[4/5] 構造化filterを確認します'
search filtered "{\"query\":\"${ranking_query}\",\"mode\":\"hybrid\",\"top_k\":5,${ranking_filters}}"
jq -e 'all(.hits[]; .document_type == "support_case")' "${tmp_dir}/filtered.json" >/dev/null

echo '[5/5] 保証条件の文脈復元を確認します'
search context '{"query":"WM-A410の無償交換が認められる条件と、対象外になる場合","mode":"hybrid_context","top_k":5}'
jq -e '[.hits[] | select(.parent_id == "warranty-context-wm-a410")][0].context_chunks | map(.id) == ["warranty-context-wm-a410-1", "warranty-context-wm-a410-2", "warranty-context-wm-a410-3"]' "${tmp_dir}/context.json" >/dev/null

echo '第5章の主要な実測結果を再現できました。'
