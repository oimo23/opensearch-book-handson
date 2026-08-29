#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

for command_name in aws node npm npx jq curl; do
  require_command "${command_name}"
done

jq empty "${PROJECT_DIR}/osis/syn10m-autoopt32x.index.json"
jq empty "${PROJECT_DIR}/osis/synthetic-10m-autoopt32x.pipeline.json"

[[ "${AWS_REGION}" == "ap-northeast-1" ]] \
  || die "このハンズオンは共有S3データと検証済み構成に合わせ、AWS_REGION=ap-northeast-1で実行してください。"

if [[ "${DRY_RUN}" == "1" ]]; then
  log "dry-run: AWS認証とS3データの確認を省略しました。"
  exit 0
fi

account_id="$(aws sts get-caller-identity --query Account --output text)"
[[ -n "${account_id}" && "${account_id}" != "None" ]] || die "AWSアカウントを取得できません。"
log "AWS account=${account_id} region=${AWS_REGION}"

aws cloudformation describe-stacks \
  --stack-name CDKToolkit \
  --region "${AWS_REGION}" >/dev/null 2>&1 \
  || die "CDK bootstrap stackが見つかりません。先にcdk bootstrapを実行してください。"
log "CDK bootstrap済みであることを確認しました。"

aws s3api head-object \
  --bucket opensearch-book-handson-data-153766774185 \
  --key synthetic-cohere-like-parquet-10m-v2/data/part-00000.parquet \
  --region "${AWS_REGION}" >/dev/null

log "共有データセットへアクセスできます。"
