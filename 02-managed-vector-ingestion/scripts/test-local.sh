#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

for file in "${PROJECT_DIR}"/scripts/*.sh "${PROJECT_DIR}"/osis/*.sh "${PROJECT_DIR}"/queries/*.sh; do
  bash -n "${file}"
done

for file in "${PROJECT_DIR}"/osis/*.json; do
  jq empty "${file}"
done
for file in "${PROJECT_DIR}"/queries/*.json; do
  if head -n 1 "${file}" | grep -Eq '^(GET|POST|PUT|DELETE) '; then
    tail -n +2 "${file}" | jq empty
  else
    jq empty "${file}"
  fi
done

if grep -R -En \
  --exclude-dir=node_modules \
  --exclude-dir=cdk.out \
  --exclude=test-local.sh \
  'search-handson-vector|arn:aws:iam::153766774185|realworld-opensearch-vector-data|__ACCOUNT_ID__' \
  "${PROJECT_DIR}"; then
  echo "著者環境に依存する実行時設定が残っています。" >&2
  exit 1
fi

cd "${PROJECT_DIR}"
npm run build

CDK_OUTDIR="${TMP_DIR}/cdk.out" \
CDK_DEFAULT_ACCOUNT=111122223333 \
CDK_DEFAULT_REGION=us-west-2 \
npx ts-node --prefer-ts-exts bin/app.ts \
  -c allowedCidrs=203.0.113.10/32

template="${TMP_DIR}/cdk.out/ManagedVectorIngestionStack.template.json"
grep -q '111122223333' "${template}"
if grep -Eq 'arn:aws:iam::153766774185|search-handson-vector' "${template}"; then
  echo "CDK templateに著者環境の値が残っています。" >&2
  exit 1
fi

DRY_RUN=1 AWS_REGION=ap-northeast-1 MODE=smoke "${SCRIPT_DIR}/run.sh"
jq -e '
  .["book-vector-ingestion"].source.s3.scan.buckets[0].bucket.filter.include_prefix[0]
    == "synthetic-cohere-like-parquet-10m-v2/data/part-00000.parquet"
  and .["book-vector-ingestion"].source.s3.aws.region == "ap-northeast-1"
  and .["book-vector-ingestion"].sink[0].opensearch.aws.region == "ap-northeast-1"
' "${PROJECT_DIR}/.handson/book-vector-10m-32x.pipeline.json" >/dev/null
DRY_RUN=1 CONFIRM_DESTROY=yes "${SCRIPT_DIR}/destroy.sh"

echo "local reproducibility checks: ok"
