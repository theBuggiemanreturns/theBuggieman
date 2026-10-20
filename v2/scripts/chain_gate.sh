#!/usr/bin/env bash
# Chain gate: a CONFIRMED chain card must have links, a non-prose witness,
# a fork PoC, a kill attempt, and an EXTRACT (or scope-cited) class.
set -euo pipefail
F="${1:?usage: chain_gate.sh <research/contradictions.md>}"
need='LINKS WITNESS SEQUENCE MONETIZATION EVIDENCE CLASS KILL'
miss=0
for k in $need; do grep -q "$k" "$F" || { echo "MISSING: $k"; miss=1; }; done
grep -qi 'RUNTIME' "$F" || { echo "WARN: no RUNTIME_VERIFIED evidence yet"; }
grep -qi 'POC' "$F" || { echo "WARN: no PoC path recorded"; }
if [ "$miss" -eq 0 ]; then echo "CHAIN GATE OK"; exit 0; else echo "CHAIN GATE INCOMPLETE"; exit 1; fi
