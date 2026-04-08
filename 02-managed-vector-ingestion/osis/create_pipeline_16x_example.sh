#!/usr/bin/env bash
set -euo pipefail

PIPELINE_NAME="${PIPELINE_NAME:-vectoringestion10mfaiss16x}"
REGION="${AWS_REGION:-ap-northeast-1}"
CONFIG_PATH="$(cd "$(dirname "$0")" && pwd)/synthetic-10m-faiss16x.pipeline.json"

cat <<EOF
このスクリプトは、10M / Faiss + on_disk + 16x 用 pipeline を
CLI で作る時の例です。まだ自動では実行しません。

必要なら次のコマンドを手元で実行してください。

aws osis create-pipeline \\
  --region ${REGION} \\
  --pipeline-name ${PIPELINE_NAME} \\
  --min-units 4 \\
  --max-units 8 \\
  --pipeline-configuration-body file://${CONFIG_PATH}
EOF
