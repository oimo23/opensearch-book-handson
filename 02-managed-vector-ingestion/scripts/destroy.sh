#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

if [[ "${DRY_RUN}" != "1" && "${CONFIRM_DESTROY:-}" != "yes" ]]; then
  die "index、pipeline、OpenSearchドメインを削除します。CONFIRM_DESTROY=yes を指定してください。"
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: pipeline=${PIPELINE_NAME}、index=${INDEX_NAME}、stack=${STACK_NAME}を削除します。"
  exit 0
fi

endpoint="$(domain_endpoint 2>/dev/null || true)"
status="$(pipeline_status || true)"
if [[ -n "${status}" ]]; then
  case "${status}" in
    ACTIVE|STARTING|UPDATING)
      aws osis stop-pipeline --pipeline-name "${PIPELINE_NAME}" --region "${AWS_REGION}" >/dev/null
      wait_for_pipeline_status STOPPED 1800
      ;;
  esac
  aws osis delete-pipeline --pipeline-name "${PIPELINE_NAME}" --region "${AWS_REGION}" >/dev/null
  log "pipeline=${PIPELINE_NAME} の削除を要求しました。"
  wait_for_pipeline_deleted 1800
fi

if [[ -n "${endpoint}" ]] && curl -fsS "${endpoint}/${INDEX_NAME}/_mapping" >/dev/null 2>&1; then
  curl -fsS -X DELETE "${endpoint}/${INDEX_NAME}" | jq -e '.acknowledged == true' >/dev/null
  log "index=${INDEX_NAME} を削除しました。"
fi

cd "${PROJECT_DIR}"
account_id="$(aws sts get-caller-identity --query Account --output text)"
CDK_DEFAULT_ACCOUNT="${account_id}" \
CDK_DEFAULT_REGION="${AWS_REGION}" \
npx cdk destroy --force -c allowedCidrs=127.0.0.1/32
log "stack=${STACK_NAME} の削除を要求しました。"
