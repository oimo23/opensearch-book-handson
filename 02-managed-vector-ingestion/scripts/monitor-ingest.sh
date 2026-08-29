#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

TARGET_COUNT="${TARGET_COUNT:-50000}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-60}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-21600}"
endpoint="$(domain_endpoint)"

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: ${INDEX_NAME} が${TARGET_COUNT}件へ到達するまで監視し、pipelineを停止します。"
  exit 0
fi

started="$(date +%s)"
while true; do
  status="$(pipeline_status || true)"
  count="$(curl -fsS "${endpoint}/${INDEX_NAME}/_count" | jq -er '.count')"
  log "pipeline=${status:-NOT_FOUND} count=${count}/${TARGET_COUNT}"

  if (( count >= TARGET_COUNT )); then
    if [[ "${status}" != "STOPPED" ]]; then
      aws osis stop-pipeline \
        --pipeline-name "${PIPELINE_NAME}" \
        --region "${AWS_REGION}" >/dev/null
    fi
    break
  fi

  case "${status}" in
    STARTING|ACTIVE|UPDATING) ;;
    *) die "目標件数へ到達する前にpipelineが実行状態を外れました: ${status:-NOT_FOUND}" ;;
  esac

  if (( $(date +%s) - started >= MAX_WAIT_SECONDS )); then
    die "投入完了を待機中にタイムアウトしました。"
  fi
  sleep "${INTERVAL_SECONDS}"
done

wait_for_pipeline_status STOPPED 1800
