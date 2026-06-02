#!/usr/bin/env bash
# Resolve hackmd.io URL or raw id → internal note id (stdout). Team path on stderr as team:PATH.
set -euo pipefail

INPUT="${1:?usage: resolve-note.sh <url-or-note-id>}"

if [[ "$INPUT" =~ ^https?://hackmd\.io/@([^/]+)/([^/?#]+) ]]; then
  TEAM="${BASH_REMATCH[1]}"
  SHORT="${BASH_REMATCH[2]}"
  command -v jq >/dev/null || { echo "ERROR: jq required for team URLs" >&2; exit 2; }
  ID="$(hackmd-cli team-notes --teamPath="$TEAM" --output=json \
    | jq -r --arg s "$SHORT" '[.[] | select(.shortId == $s or .id == $s)][0].id // empty')"
  [[ -n "$ID" ]] || { echo "ERROR: no note matching shortId=$SHORT in team $TEAM" >&2; exit 2; }
  echo "$ID"
  echo "team:$TEAM" >&2
elif [[ "$INPUT" =~ ^https?://hackmd\.io/([^/?#]+) ]]; then
  echo "${BASH_REMATCH[1]}"
elif [[ "$INPUT" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "$INPUT"
else
  echo "ERROR: cannot parse note reference: $INPUT" >&2
  exit 2
fi
