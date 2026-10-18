#!/usr/bin/env bash
# Batch read-only deployment reconnaissance.
#
# Requires: cast (Foundry), jq, python3
# Usage:
#   ./trace_deployment.sh <address> <rpc-url> <creation-tx-hash> [output-root]
#
# Direct contract creation input starts with init code, not a function selector.
# Factory creation input starts with a callable selector but may require debug
# traces/events to identify internal CREATE/CREATE2 outputs. Address-shaped words
# from either form are heuristic candidates only.

set -euo pipefail

ADDRESS="${1:?Usage: trace_deployment.sh <address> <rpc-url> <creation-tx-hash> [output-root]}"
RPC="${2:?Usage: trace_deployment.sh <address> <rpc-url> <creation-tx-hash> [output-root]}"
TXHASH="${3:?Usage: trace_deployment.sh <address> <rpc-url> <creation-tx-hash> [output-root]}"
OUT_ROOT="${4:-onchain-recon-output}"

if [[ ! "$ADDRESS" =~ ^0x[0-9a-fA-F]{40}$ ]]; then
  echo "Invalid contract address: $ADDRESS" >&2
  exit 2
fi
if [[ ! "$TXHASH" =~ ^0x[0-9a-fA-F]{64}$ ]]; then
  echo "Invalid transaction hash: $TXHASH" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$OUT_ROOT/$ADDRESS"
mkdir -p "$OUT_DIR"

echo "== Fetching deployment transaction and receipt =="
cast tx "$TXHASH" --rpc-url "$RPC" --json > "$OUT_DIR/creation_tx.json"
cast receipt "$TXHASH" --rpc-url "$RPC" --json > "$OUT_DIR/creation_receipt.json"

INPUT=$(jq -r '.input // empty' "$OUT_DIR/creation_tx.json")
TX_TO=$(jq -r '.to // empty' "$OUT_DIR/creation_tx.json")
CREATED=$(jq -r '.contractAddress // .contract_address // empty' "$OUT_DIR/creation_receipt.json")

if [ -z "$INPUT" ] || [ "$INPUT" = "0x" ]; then
  echo "Transaction has no deployment/factory calldata." >&2
  exit 1
fi

if [ -z "$TX_TO" ] || [ "$TX_TO" = "null" ]; then
  echo "Direct creation detected: input begins with init code."
  if [ -n "$CREATED" ] && [ "${CREATED,,}" != "${ADDRESS,,}" ]; then
    echo "WARNING: receipt created $CREATED, not requested $ADDRESS."
  fi
  echo "Constructor boundaries require verified creation bytecode/metadata."
else
  SELECTOR="${INPUT:0:10}"
  echo "Factory/runtime call detected: to=$TX_TO selector=$SELECTOR"
  if [ "$SELECTOR" = "0xac9650d8" ]; then
    echo "Standard multicall(bytes[]) selector detected; sub-call boundaries are not decoded."
  else
    cast 4byte "$SELECTOR" 2>/dev/null || echo "(selector not found in 4byte registry)"
  fi
  echo "Internal CREATE/CREATE2 products may require debug traces or emitted events."
fi

echo "== Extracting heuristic candidate addresses =="
EXTRACT_ARGS=("$INPUT")
if [ -n "$TX_TO" ] && [ "$TX_TO" != "null" ]; then
  EXTRACT_ARGS+=(--skip-selector)
else
  echo "WARNING: direct-creation constructor alignment is unknown without creation"
  echo "bytecode metadata; treat this shortlist as especially incomplete/noisy."
fi
python3 "$SCRIPT_DIR/extract_candidate_addresses.py" "${EXTRACT_ARGS[@]}" \
  | tee "$OUT_DIR/candidates_raw.txt"

grep -oE '0x[0-9a-fA-F]{40}' "$OUT_DIR/candidates_raw.txt" | sort -u \
  > "$OUT_DIR/candidates.txt" || true

if [ ! -s "$OUT_DIR/candidates.txt" ]; then
  echo "No address-shaped words found. This does not prove there are no runtime dependencies."
  exit 0
fi

echo -e "address\thas_code\tcode_size_bytes" > "$OUT_DIR/graph.tsv"
while read -r CANDIDATE; do
  CODE=$(cast code "$CANDIDATE" --rpc-url "$RPC")
  if [ "$CODE" = "0x" ]; then
    echo -e "${CANDIDATE}\tno (EOA, unset, or predeploy at current block)\t0" >> "$OUT_DIR/graph.tsv"
  else
    SIZE=$(( (${#CODE} - 2) / 2 ))
    echo -e "${CANDIDATE}\tyes\t${SIZE}" >> "$OUT_DIR/graph.tsv"
  fi
done < "$OUT_DIR/candidates.txt"

echo "== Result: $OUT_DIR/graph.tsv =="
if command -v column >/dev/null 2>&1; then
  column -t -s $'\t' "$OUT_DIR/graph.tsv"
else
  sed -n '1,200p' "$OUT_DIR/graph.tsv"
fi

echo "Next: confirm material candidates with ABI/source/storage/log evidence, resolve"
echo "their controllers, and merge confirmed edges into onchain-graph.md."
