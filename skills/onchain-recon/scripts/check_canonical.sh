#!/usr/bin/env bash
# Diff local Solidity files against cached upstream templates.
# EXACT_UPSTREAM lowers source-diff priority; CUSTOM_OR_MODIFIED raises it.
# Neither label determines operational control, integration risk, or scope.
# Record the reported upstream commit as evidence.
#
# Requires: git, diff (both standard)
#
# Usage:
#   ./check_canonical.sh <local-source-dir-or-file> [known-repos-file]
#
# known-repos-file format (one per line): <repo-url> <ref> <path-prefix-in-repo>
#   e.g.  https://github.com/Uniswap/v4-core main src/
#   Defaults to references/known-templates.txt next to this script.

set -euo pipefail

TARGET="${1:?Usage: check_canonical.sh <local-source-dir-or-file> [known-repos-file]}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_LIST="${2:-$SCRIPT_DIR/../references/known-templates.txt}"
CACHE_DIR="${ONCHAIN_RECON_CACHE:-$HOME/.cache/onchain-recon/repos}"
mkdir -p "$CACHE_DIR"

if [ ! -f "$REPO_LIST" ]; then
  echo "No known-repos file at $REPO_LIST — nothing to compare against."
  exit 1
fi

echo -e "file\tstatus\tmatched_against\tupstream_commit"

# Cache by repository URL, then force the requested ref before every run.
# This supports branch, tag, and commit refs without silently reusing stale code.
mapfile -t REPO_LINES < "$REPO_LIST"
for LINE in "${REPO_LINES[@]}"; do
  [ -z "$LINE" ] && continue
  [[ "$LINE" =~ ^# ]] && continue
  read -r URL REF PREFIX EXTRA <<< "$LINE"
  if [ -z "${URL:-}" ] || [ -z "${REF:-}" ] || [ -z "${PREFIX:-}" ] || [ -n "${EXTRA:-}" ]; then
    echo "Invalid known-repos entry: $LINE" >&2
    exit 1
  fi
  NAME=$(basename "$URL" .git)
  URL_KEY=$(printf '%s' "$URL" | cksum | awk '{print $1}')
  REPO_DIR="$CACHE_DIR/${NAME}-${URL_KEY}"
  if [ ! -d "$REPO_DIR/.git" ]; then
    git clone --quiet --no-checkout "$URL" "$REPO_DIR"
  elif [ "$(git -C "$REPO_DIR" remote get-url origin)" != "$URL" ]; then
    echo "Cache remote mismatch at $REPO_DIR" >&2
    exit 1
  fi
  git -C "$REPO_DIR" fetch --quiet --depth 1 origin "$REF" 2>/dev/null \
    || git -C "$REPO_DIR" fetch --quiet origin "$REF"
  git -C "$REPO_DIR" checkout --quiet --detach FETCH_HEAD
done

find_files() {
  if [ -d "$TARGET" ]; then
    find "$TARGET" -name '*.sol'
  else
    echo "$TARGET"
  fi
}

while read -r FILE; do
  BASENAME=$(basename "$FILE")
  MATCHED="no"
  for LINE in "${REPO_LINES[@]}"; do
    [ -z "$LINE" ] && continue
    [[ "$LINE" =~ ^# ]] && continue
    read -r URL REF PREFIX <<< "$LINE"
    NAME=$(basename "$URL" .git)
    URL_KEY=$(printf '%s' "$URL" | cksum | awk '{print $1}')
    REPO_DIR="$CACHE_DIR/${NAME}-${URL_KEY}"
    CANDIDATE=$(find "$REPO_DIR/$PREFIX" -name "$BASENAME" 2>/dev/null | head -1)
    if [ -n "$CANDIDATE" ] && diff -q "$FILE" "$CANDIDATE" > /dev/null 2>&1; then
      COMMIT=$(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")
      echo -e "${FILE}\tEXACT_UPSTREAM\t${NAME}\t${COMMIT}"
      MATCHED="yes"
      break
    fi
  done
  if [ "$MATCHED" = "no" ]; then
    echo -e "${FILE}\tCUSTOM_OR_MODIFIED\t-\t-"
  fi
done < <(find_files)
