#!/usr/bin/env bash
# Batch every zero-argument view/pure function from an ABI.
#
# Requires: cast (Foundry), jq
# Usage:
#   ./sweep_view_functions.sh <address> <rpc-url> <abi.json> [block]
#
# The ABI may be a raw JSON array or an object with an "abi" field. Calls are
# read-only. Failures are recorded per function so one reverting getter does not
# erase the rest of the evidence.

set -euo pipefail

ADDRESS="${1:?Usage: sweep_view_functions.sh <address> <rpc-url> <abi.json> [block]}"
RPC="${2:?Usage: sweep_view_functions.sh <address> <rpc-url> <abi.json> [block]}"
ABI_FILE="${3:?Usage: sweep_view_functions.sh <address> <rpc-url> <abi.json> [block]}"
BLOCK="${4:-}"

FUNCS=$(jq -r '
  (if type == "object" and has("abi") then .abi else . end)
  | .[]
  | select(.type == "function")
  | select(.stateMutability == "view" or .stateMutability == "pure")
  | select((.inputs | length) == 0)
  | [.name, ([.outputs[].type] | join(","))]
  | @tsv
' "$ABI_FILE")

if [ -z "$FUNCS" ]; then
  echo "No zero-argument view/pure functions found in $ABI_FILE."
  exit 0
fi

echo -e "signature\tblock\tresult"
while IFS=$'\t' read -r FN OUT_TYPES; do
  SIG="${FN}()(${OUT_TYPES})"
  CALL_ARGS=(call "$ADDRESS" "$SIG" --rpc-url "$RPC")
  if [ -n "$BLOCK" ]; then
    CALL_ARGS+=(--block "$BLOCK")
  fi
  RESULT=$(cast "${CALL_ARGS[@]}" 2>&1) || RESULT="<call reverted or failed: ${RESULT}>"
  RESULT=${RESULT//$'\t'/ }
  RESULT=${RESULT//$'\n'/\\n}
  echo -e "${SIG}\t${BLOCK:-latest}\t${RESULT}"
done <<< "$FUNCS"
