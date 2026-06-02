#!/usr/bin/env bash
# Build standalone HTML → HackMD markup and create a personal note.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INPUT="${1:-/tmp/viz.html}"
OUTPUT="${2:-/tmp/viz-hackmd.html}"
TITLE="${VIZ_TITLE:-Visualization}"

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: input not found: $INPUT" >&2
  exit 2
fi

python3 "$SKILL_DIR/scripts/to-hackmd.py" --strict "$INPUT" "$OUTPUT"

# Optional Custom CSS reminder in note body
BODY="$(cat "$OUTPUT")"
REMINDER='<!-- Enable Custom CSS preview: toolbar paintbrush → Custom CSS -->'
if [[ "$BODY" != *"Custom CSS"* ]]; then
  BODY="${REMINDER}
${BODY}"
fi

hackmd-cli notes create \
  --title="$TITLE" \
  --readPermission=owner \
  --writePermission=owner \
  --content="$BODY"

echo "Reminder: open the note and enable Custom CSS preview (paintbrush icon)."
