#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DOMAIN_ENDPOINT:-}" ]]; then
  echo "DOMAIN_ENDPOINT is required." >&2
  exit 1
fi

INDEX_NAME="${INDEX_NAME:-syn10m_s3vector}"
ROUNDS="${ROUNDS:-10}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUERY_FILE="${SCRIPT_DIR}/dev_tools_query_syn10m_full.json"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

if [[ "${DOMAIN_ENDPOINT}" == http://* || "${DOMAIN_ENDPOINT}" == https://* ]]; then
  BASE_URL="${DOMAIN_ENDPOINT%/}"
else
  BASE_URL="https://${DOMAIN_ENDPOINT%/}"
fi

# The source file starts with a Dev Tools request line. Request all k=10 results.
tail -n +2 "${QUERY_FILE}" | jq '.size = 10' > "${TMP_DIR}/query.json"

echo "Warmup: ${INDEX_NAME}"
WARMUP_SECONDS="$(
  curl -fsS \
    -o "${TMP_DIR}/warmup.json" \
    -w '%{time_total}' \
    -X GET "${BASE_URL}/_plugins/_knn/warmup/${INDEX_NAME}"
)"
echo "warmup_seconds=${WARMUP_SECONDS}"

: > "${TMP_DIR}/took.txt"
for ((i = 1; i <= ROUNDS; i++)); do
  RESPONSE_FILE="${TMP_DIR}/response-${i}.json"
  curl -fsS \
    -X POST "${BASE_URL}/${INDEX_NAME}/_search" \
    -H "Content-Type: application/json" \
    --data-binary "@${TMP_DIR}/query.json" \
    > "${RESPONSE_FILE}"

  TOOK="$(jq -er '.took' "${RESPONSE_FILE}")"
  echo "${TOOK}" >> "${TMP_DIR}/took.txt"
  printf 'run=%d took_ms=%s\n' "${i}" "${TOOK}"
done

jq -s '
  sort as $values
  | length as $count
  | {
      runs: $count,
      mean_ms: (((add / $count) * 10 | round) / 10),
      p50_ms: (
        if ($count % 2) == 1 then
          $values[($count / 2 | floor)]
        else
          (($values[$count / 2 - 1] + $values[$count / 2]) / 2)
        end
      ),
      min_ms: $values[0],
      max_ms: $values[-1]
    }
' "${TMP_DIR}/took.txt"
