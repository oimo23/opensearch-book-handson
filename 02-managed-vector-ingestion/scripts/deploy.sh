#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_cost_confirmation

if [[ "${DRY_RUN}" == "1" ]]; then
  default_domain_name="handson-vector-reader"
else
  default_domain_name="handson-vector-$(aws sts get-caller-identity --query Account --output text)"
fi
DOMAIN_NAME="${DOMAIN_NAME:-${default_domain_name}}"
INSTANCE_TYPE="${INSTANCE_TYPE:-or2.xlarge.search}"
INSTANCE_COUNT="${INSTANCE_COUNT:-1}"
EBS_VOLUME_SIZE="${EBS_VOLUME_SIZE:-512}"
ENABLE_S3_VECTORS="${ENABLE_S3_VECTORS:-false}"
ENABLE_GPU_ACCELERATION="${ENABLE_GPU_ACCELERATION:-true}"

cdk_args=(
  -c "domainName=${DOMAIN_NAME}"
  -c "instanceType=${INSTANCE_TYPE}"
  -c "instanceCount=${INSTANCE_COUNT}"
  -c "ebsVolumeSize=${EBS_VOLUME_SIZE}"
  -c "enableS3Vectors=${ENABLE_S3_VECTORS}"
  -c "enableGpuAcceleration=${ENABLE_GPU_ACCELERATION}"
)
if [[ -n "${ALLOWED_CIDRS:-}" ]]; then
  cdk_args+=( -c "allowedCidrs=${ALLOWED_CIDRS}" )
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: npm ci"
  printf '[handson] dry-run: npx cdk deploy --require-approval never'
  printf ' %q' "${cdk_args[@]}"
  printf '\n'
  exit 0
fi

cd "${PROJECT_DIR}"
npm ci
account_id="$(aws sts get-caller-identity --query Account --output text)"
CDK_DEFAULT_ACCOUNT="${account_id}" \
CDK_DEFAULT_REGION="${AWS_REGION}" \
npx cdk deploy --require-approval never "${cdk_args[@]}"

log "DomainEndpoint=$(domain_endpoint)"
log "IngestionRoleArn=$(ingestion_role_arn)"
