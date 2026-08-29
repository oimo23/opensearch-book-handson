#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

TEMPLATE_PATH="${TEMPLATE_PATH:-${PROJECT_DIR}/osis/synthetic-10m-autoopt32x.pipeline.json}"
RENDERED_CONFIG="${STATE_DIR}/${PIPELINE_NAME}.pipeline.json"
render_pipeline "${TEMPLATE_PATH}" "${RENDERED_CONFIG}"

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: pipeline設定を${RENDERED_CONFIG}へ生成しました。"
  log "dry-run: aws osis validate-pipeline / create-pipeline ${PIPELINE_NAME}"
  exit 0
fi

if pipeline_status >/dev/null 2>&1; then
  die "pipeline=${PIPELINE_NAME} はすでに存在します。再投入前にscripts/destroy.shで削除してください。"
fi

validation_path="${STATE_DIR}/${PIPELINE_NAME}.validation.json"
aws osis validate-pipeline \
  --pipeline-configuration-body "file://${RENDERED_CONFIG}" \
  --region "${AWS_REGION}" \
  --output json > "${validation_path}"
jq -e '.isValid == true' "${validation_path}" >/dev/null \
  || { jq . "${validation_path}" >&2; die "pipeline設定のvalidationに失敗しました。"; }

aws osis create-pipeline \
  --pipeline-name "${PIPELINE_NAME}" \
  --min-units "${MIN_UNITS}" \
  --max-units "${MAX_UNITS}" \
  --pipeline-role-arn "$(ingestion_role_arn)" \
  --pipeline-configuration-body "file://${RENDERED_CONFIG}" \
  --region "${AWS_REGION}" >/dev/null

wait_for_pipeline_status ACTIVE 1800
