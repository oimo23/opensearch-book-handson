#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

export PIPELINE_NAME="${PIPELINE_NAME:-book-s3vector-10m}"
export INDEX_NAME="${INDEX_NAME:-syn10m_s3vector}"
export TARGET_COUNT="${TARGET_COUNT:-10000000}"

exec "${PROJECT_DIR}/scripts/monitor-ingest.sh"
