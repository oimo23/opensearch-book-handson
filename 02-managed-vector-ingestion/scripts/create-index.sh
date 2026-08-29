#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

INDEX_CONFIG="${INDEX_CONFIG:-${PROJECT_DIR}/osis/syn10m-autoopt32x.index.json}"
EXPECTED_COMPRESSION="${EXPECTED_COMPRESSION-32x}"
EXPECTED_ENGINE="${EXPECTED_ENGINE-faiss}"
EXPECTED_MODE="${EXPECTED_MODE-on_disk}"
EXPECTED_DIMENSION="${EXPECTED_DIMENSION:-1024}"
endpoint="$(domain_endpoint)"

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: PUT ${endpoint}/${INDEX_NAME} <- ${INDEX_CONFIG}"
  exit 0
fi

if curl -fsS "${endpoint}/${INDEX_NAME}/_mapping" >/dev/null 2>&1; then
  log "index=${INDEX_NAME} はすでに存在します。"
else
  curl -fsS -X PUT \
    "${endpoint}/${INDEX_NAME}" \
    -H 'Content-Type: application/json' \
    --data-binary "@${INDEX_CONFIG}" | jq -e '.acknowledged == true' >/dev/null
  log "index=${INDEX_NAME} を作成しました。"
fi

mapping_path="${STATE_DIR}/${INDEX_NAME}.mapping.json"
curl -fsS "${endpoint}/${INDEX_NAME}/_mapping" > "${mapping_path}"

jq -e --arg index "${INDEX_NAME}" --argjson expected "${EXPECTED_DIMENSION}" \
  '.[$index].mappings.properties.vector.dimension == $expected' \
  "${mapping_path}" >/dev/null
log "dimension=${EXPECTED_DIMENSION} を確認しました。"

if [[ -n "${EXPECTED_COMPRESSION}" ]]; then
  jq -e --arg index "${INDEX_NAME}" --arg expected "${EXPECTED_COMPRESSION}" \
    '.[$index].mappings.properties.vector.compression_level == $expected' \
    "${mapping_path}" >/dev/null
  log "compression_level=${EXPECTED_COMPRESSION} を確認しました。"
fi

if [[ -n "${EXPECTED_ENGINE}" ]]; then
  jq -e --arg index "${INDEX_NAME}" --arg expected "${EXPECTED_ENGINE}" \
    '.[$index].mappings.properties.vector.method.engine == $expected' \
    "${mapping_path}" >/dev/null
  log "engine=${EXPECTED_ENGINE} を確認しました。"
fi

if [[ -n "${EXPECTED_MODE}" ]]; then
  jq -e --arg index "${INDEX_NAME}" --arg expected "${EXPECTED_MODE}" \
    '.[$index].mappings.properties.vector.mode == $expected' \
    "${mapping_path}" >/dev/null
  log "mode=${EXPECTED_MODE} を確認しました。"
fi
