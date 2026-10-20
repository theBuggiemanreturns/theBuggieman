#!/usr/bin/env bash
# Scaffold the research workspace for a v2 run.
set -euo pipefail
T="${1:?usage: scaffold.sh <target-dir>}"
R="$T/research"
mkdir -p "$R/experiments"
[ -f "$R/scope.md" ]        || printf '# Scope\nMode: hunt|audit\nAuthorization: UNKNOWN\nEnvironment: READ_ONLY_PRODUCTION\nLive exploitation: NO\nIn scope:\nOut of scope:\nKnown issues:\nSeverity rubric (verbatim program lines):\n' > "$R/scope.md"
[ -f "$R/NOW.md" ]          || printf '# NOW\nPhase:\nMode:\nDeviations from defaults (what + why):\n' > "$R/NOW.md"
[ -f "$R/primitives.md" ]   || cp "$(dirname "$0")/../templates/primitives.md" "$R/primitives.md"
[ -f "$R/contradictions.md" ] || printf '# Chain cards\n' > "$R/contradictions.md"
[ -f "$R/report.md" ]       || printf '# Report\n' > "$R/report.md"
echo "scaffolded $R"
