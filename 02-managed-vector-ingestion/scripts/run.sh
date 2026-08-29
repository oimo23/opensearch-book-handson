#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

MODE="${MODE:-smoke}"
case "${MODE}" in
  smoke)
    export SOURCE_PREFIX="${SOURCE_PREFIX:-synthetic-cohere-like-parquet-10m-v2/data/part-00000.parquet}"
    export TARGET_COUNT="${TARGET_COUNT:-50000}"
    ;;
  full)
    [[ "${DRY_RUN:-0}" == "1" || "${CONFIRM_10M_INGEST:-}" == "yes" ]] \
      || { echo "CONFIRM_10M_INGEST=yes を指定してください。" >&2; exit 1; }
    export TARGET_COUNT=10000000
    ;;
  *)
    echo "MODEはsmokeまたはfullを指定してください。" >&2
    exit 1
    ;;
esac

cleanup_notice() {
  local exit_code=$?
  if (( exit_code != 0 )) && [[ "${DRY_RUN:-0}" != "1" ]]; then
    printf '\n途中で失敗しました。作成済みリソースを確認し、次のコマンドで削除してください。\n' >&2
    printf 'CONFIRM_DESTROY=yes %q/destroy.sh\n' "${SCRIPT_DIR}" >&2
  fi
  exit "${exit_code}"
}
trap cleanup_notice EXIT

"${SCRIPT_DIR}/preflight.sh"
"${SCRIPT_DIR}/deploy.sh"
"${SCRIPT_DIR}/create-index.sh"
"${SCRIPT_DIR}/create-pipeline.sh"
"${SCRIPT_DIR}/monitor-ingest.sh"
EXPECTED_COUNT="${TARGET_COUNT}" "${SCRIPT_DIR}/verify.sh"

trap - EXIT

printf '\n検証が完了しました。確認後、次のコマンドで課金リソースを削除してください。\n'
printf 'CONFIRM_DESTROY=yes %q/destroy.sh\n' "${SCRIPT_DIR}"
