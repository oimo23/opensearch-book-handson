#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

EXPECTED_COUNT="${EXPECTED_COUNT:-${TARGET_COUNT:-50000}}"
endpoint="$(domain_endpoint)"
result_path="${STATE_DIR}/verification.json"

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: count、mapping、k-NN queryを検証します。"
  exit 0
fi

count="$(curl -fsS "${endpoint}/${INDEX_NAME}/_count" | jq -er '.count')"
(( count >= EXPECTED_COUNT )) || die "件数が不足しています: ${count}/${EXPECTED_COUNT}"

mapping="$(curl -fsS "${endpoint}/${INDEX_NAME}/_mapping")"
compression="$(jq -er --arg index "${INDEX_NAME}" \
  '.[$index].mappings.properties.vector.compression_level' <<< "${mapping}")"
[[ "${compression}" == "32x" ]] || die "compression_levelが32xではありません: ${compression}"
engine="$(jq -er --arg index "${INDEX_NAME}" \
  '.[$index].mappings.properties.vector.method.engine' <<< "${mapping}")"
[[ "${engine}" == "faiss" ]] || die "engineがfaissではありません: ${engine}"
mode="$(jq -er --arg index "${INDEX_NAME}" \
  '.[$index].mappings.properties.vector.mode' <<< "${mapping}")"
[[ "${mode}" == "on_disk" ]] || die "modeがon_diskではありません: ${mode}"
dimension="$(jq -er --arg index "${INDEX_NAME}" \
  '.[$index].mappings.properties.vector.dimension' <<< "${mapping}")"
[[ "${dimension}" == "1024" ]] || die "dimensionが1024ではありません: ${dimension}"

query_path="${STATE_DIR}/query.json"
tail -n +2 "${PROJECT_DIR}/queries/dev_tools_query_syn10m_full.json" \
  | jq '.size = 10' > "${query_path}"

search_path="${STATE_DIR}/search-response.json"
curl -fsS -X POST \
  "${endpoint}/${INDEX_NAME}/_search" \
  -H 'Content-Type: application/json' \
  --data-binary "@${query_path}" > "${search_path}"

jq -e '.timed_out == false and (.hits.hits | length > 0)' "${search_path}" >/dev/null
jq -n \
  --arg index "${INDEX_NAME}" \
  --argjson count "${count}" \
  --arg compression "${compression}" \
  --slurpfile search "${search_path}" \
  '{
    index: $index,
    count: $count,
    compression_level: $compression,
    engine: "faiss",
    mode: "on_disk",
    dimension: 1024,
    search: {
      took: $search[0].took,
      timed_out: $search[0].timed_out,
      top_hit: $search[0].hits.hits[0]
    }
  }' > "${result_path}"

log "検証に成功しました: ${result_path}"
jq '{index, count, compression_level, engine, mode, dimension, search: {took, timed_out, top_id: .search.top_hit._source.id}}' "${result_path}"
