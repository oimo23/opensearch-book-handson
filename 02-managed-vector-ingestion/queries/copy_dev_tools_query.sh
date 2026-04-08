#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUERY_FILE="$SCRIPT_DIR/dev_tools_query_syn10m_full.json"

pbcopy < "$QUERY_FILE"
echo "Copied Dev Tools query to clipboard from: $QUERY_FILE"
