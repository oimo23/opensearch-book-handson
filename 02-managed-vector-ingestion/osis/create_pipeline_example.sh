#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PIPELINE_NAME="${PIPELINE_NAME:-book-vector-10m-2x}"
export INDEX_NAME="${INDEX_NAME:-synthetic_10m_faiss_2x}"
export TEMPLATE_PATH="${SCRIPT_DIR}/synthetic-10m-faiss2x.pipeline.json"
exec "${SCRIPT_DIR}/../scripts/create-pipeline.sh"
