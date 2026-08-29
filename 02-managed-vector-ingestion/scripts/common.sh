#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATE_DIR="${PROJECT_DIR}/.handson"

AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-ap-northeast-1}}"
export AWS_REGION
STACK_NAME="ManagedVectorIngestionStack"
PIPELINE_NAME="${PIPELINE_NAME:-book-vector-10m-32x}"
INDEX_NAME="${INDEX_NAME:-syn10m_autoopt32x}"
SOURCE_PREFIX="${SOURCE_PREFIX:-synthetic-cohere-like-parquet-10m-v2/data/}"
MIN_UNITS="${MIN_UNITS:-4}"
MAX_UNITS="${MAX_UNITS:-8}"
DRY_RUN="${DRY_RUN:-0}"

mkdir -p "${STATE_DIR}"

log() {
  printf '[handson] %s\n' "$*"
}

die() {
  printf '[handson] ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required."
}

require_cost_confirmation() {
  if [[ "${DRY_RUN}" != "1" && "${CONFIRM_AWS_COSTS:-}" != "yes" ]]; then
    die "AWS料金が発生します。内容を確認後、CONFIRM_AWS_COSTS=yes を指定してください。"
  fi
}

stack_output() {
  local output_key="$1"
  local value
  value="$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='${output_key}'].OutputValue | [0]" \
    --output text)"
  [[ -n "${value}" && "${value}" != "None" ]] \
    || die "CloudFormation output ${output_key} を取得できません。"
  printf '%s\n' "${value}"
}

domain_endpoint() {
  if [[ -n "${DOMAIN_ENDPOINT:-}" ]]; then
    printf '%s\n' "${DOMAIN_ENDPOINT%/}"
  elif [[ "${DRY_RUN}" == "1" ]]; then
    printf '%s\n' "https://search-reader-domain-abcdefghijklmnopqrstuvwxyz.${AWS_REGION}.es.amazonaws.com"
  else
    stack_output DomainEndpoint
  fi
}

ingestion_role_arn() {
  if [[ -n "${INGESTION_ROLE_ARN:-}" ]]; then
    printf '%s\n' "${INGESTION_ROLE_ARN}"
  elif [[ "${DRY_RUN}" == "1" ]]; then
    printf '%s\n' "arn:aws:iam::111122223333:role/reader-vector-ingestion"
  else
    stack_output IngestionRoleArn
  fi
}

pipeline_status() {
  aws osis get-pipeline \
    --pipeline-name "${PIPELINE_NAME}" \
    --region "${AWS_REGION}" \
    --query 'Pipeline.Status' \
    --output text 2>/dev/null
}

wait_for_pipeline_status() {
  local expected="$1"
  local timeout_seconds="${2:-1800}"
  local started status
  started="$(date +%s)"

  while true; do
    status="$(pipeline_status || true)"
    log "pipeline=${PIPELINE_NAME} status=${status:-NOT_FOUND}"
    [[ "${status}" == "${expected}" ]] && return 0

    case "${status}" in
      CREATE_FAILED|UPDATE_FAILED|START_FAILED|STOP_FAILED)
        die "pipelineが失敗状態になりました: ${status}"
        ;;
    esac

    if (( $(date +%s) - started >= timeout_seconds )); then
      die "pipelineが${expected}になるまでにタイムアウトしました。"
    fi
    sleep 20
  done
}

wait_for_pipeline_deleted() {
  local timeout_seconds="${1:-1800}"
  local started status
  started="$(date +%s)"

  while true; do
    status="$(pipeline_status || true)"
    [[ -z "${status}" ]] && return 0
    log "pipeline=${PIPELINE_NAME} delete_status=${status}"
    if (( $(date +%s) - started >= timeout_seconds )); then
      die "pipelineの削除待機中にタイムアウトしました。"
    fi
    sleep 20
  done
}

render_pipeline() {
  local template_path="$1"
  local output_path="$2"
  local endpoint role_arn
  endpoint="$(domain_endpoint)"
  role_arn="$(ingestion_role_arn)"

  jq \
    --arg endpoint "${endpoint}" \
    --arg role_arn "${role_arn}" \
    --arg region "${AWS_REGION}" \
    --arg index_name "${INDEX_NAME}" \
    --arg source_prefix "${SOURCE_PREFIX}" \
    'walk(
      if type == "string" then
        gsub("__DOMAIN_ENDPOINT__"; $endpoint)
        | gsub("__INGESTION_ROLE_ARN__"; $role_arn)
        | gsub("__AWS_REGION__"; $region)
        | gsub("__INDEX_NAME__"; $index_name)
        | gsub("__SOURCE_PREFIX__"; $source_prefix)
      else . end
    )' \
    "${template_path}" > "${output_path}"

  if grep -En '__[A-Z0-9_]+__' "${output_path}" >/dev/null 2>&1; then
    grep -En '__[A-Z0-9_]+__' "${output_path}" >&2
    die "pipeline設定に未置換のプレースホルダーがあります。"
  fi
}
