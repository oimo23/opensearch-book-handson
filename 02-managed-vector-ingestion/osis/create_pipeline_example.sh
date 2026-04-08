#!/usr/bin/env bash
set -euo pipefail

PIPELINE_NAME="${PIPELINE_NAME:-vectoringestion10mfaiss2x}"
REGION="${AWS_REGION:-ap-northeast-1}"
CONFIG_PATH="$(cd "$(dirname "$0")" && pwd)/synthetic-10m-faiss2x.pipeline.json"

cat <<EOF
このスクリプトは、後から CLI で pipeline を作るための例です。
まだ自動では実行しません。

必要なら次のコマンドを手元で実行してください。

aws osis create-pipeline \\
  --region ${REGION} \\
  --pipeline-name ${PIPELINE_NAME} \\
  --min-units 4 \\
  --max-units 8 \\
  --pipeline-configuration-body file://${CONFIG_PATH}
EOF
