#!/usr/bin/env bash
# Push working content only if remote unchanged since baseline export.
# See ../README.md for the full anti-clobber contract.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  safe-sync.sh push --note-id ID --baseline-file FILE --working-file FILE [--team-path TEAM]

  1. export current remote → recheck
  2. diff baseline vs recheck (exit 1 if different)
  3. hackmd-cli notes update | team-notes update with working-file

Exit: 0 updated, 1 conflict, 2 error
EOF
  exit 2
}

cmd="${1:-}"
shift || usage
[[ "$cmd" == "push" ]] || usage

NOTE_ID=""
BASELINE=""
WORKING=""
TEAM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --note-id) NOTE_ID="$2"; shift 2 ;;
    --baseline-file) BASELINE="$2"; shift 2 ;;
    --working-file) WORKING="$2"; shift 2 ;;
    --team-path) TEAM="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[[ -n "$NOTE_ID" && -f "$BASELINE" && -f "$WORKING" ]] || usage
command -v hackmd-cli >/dev/null || { echo "ERROR: hackmd-cli not in PATH" >&2; exit 2; }

RECHECK="$(mktemp)"
trap 'rm -f "$RECHECK"' EXIT

hackmd-cli export --noteId="$NOTE_ID" >"$RECHECK"

if ! diff -q "$BASELINE" "$RECHECK" >/dev/null 2>&1; then
  echo "CONFLICT: remote note changed since baseline export" >&2
  diff -u "$BASELINE" "$RECHECK" >&2 | head -100 || true
  exit 1
fi

if [[ -n "$TEAM" ]]; then
  hackmd-cli team-notes update \
    --teamPath="$TEAM" \
    --noteId="$NOTE_ID" \
    --content="$(cat "$WORKING")"
else
  hackmd-cli notes update --noteId="$NOTE_ID" --content="$(cat "$WORKING")"
fi

echo "OK: updated $NOTE_ID"
