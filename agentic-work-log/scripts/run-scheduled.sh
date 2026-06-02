#!/usr/bin/env bash
# Scheduled runner for agentic-work-log — requires valid config.hackmd_note_id
set -euo pipefail

LOG_DIR="${AGENTIC_WORK_LOG_LOG_DIR:-$HOME/.config/agentic-work-log/logs}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y-%m-%d).log"
CONFIG="${AGENTIC_WORK_LOG_CONFIG:-$HOME/.config/agentic-work-log/config.json}"
PROMPT='/agentic-work-log'

log() { echo "$(date -Iseconds) agentic-work-log: $*" >>"$LOG"; }

if ! command -v hackmd-cli >/dev/null; then
  log "ERROR: hackmd-cli not in PATH"
  exit 1
fi

if [[ -n "${AGENTIC_WORK_LOG_NOTE_ID:-}" ]]; then
  : # ok
elif [[ -f "$CONFIG" ]] && command -v jq >/dev/null; then
  if ! jq -e '.hackmd_note_id | length > 0' "$CONFIG" >/dev/null 2>&1; then
    log "ERROR: $CONFIG missing hackmd_note_id (set AGENTIC_WORK_LOG_NOTE_ID or fix config)"
    exit 1
  fi
else
  log "ERROR: set AGENTIC_WORK_LOG_NOTE_ID or valid $CONFIG with hackmd_note_id"
  exit 1
fi

run_claude() {
  command -v claude >/dev/null || return 1
  claude -p "$PROMPT" --allowedTools Read,Bash,Write,Edit,Agent >>"$LOG" 2>&1
}

run_cursor() {
  command -v agent >/dev/null || return 1
  agent -p "$PROMPT" >>"$LOG" 2>&1
}

run_codex() {
  command -v codex >/dev/null || return 1
  codex exec "$PROMPT" -s workspace-write >>"$LOG" 2>&1
}

run_opencode() {
  command -v opencode >/dev/null || return 1
  opencode run "$PROMPT" >>"$LOG" 2>&1
}

ran=0
if [[ -n "${AGENTIC_WORK_LOG_RUNNER:-}" ]]; then
  "run_${AGENTIC_WORK_LOG_RUNNER}" && ran=1
else
  run_cursor && ran=1 || run_claude && ran=1 || run_codex && ran=1 || run_opencode && ran=1 || true
fi

if [[ "$ran" -eq 0 ]]; then
  log "ERROR: no supported harness available (cursor/claude/codex/opencode)"
  exit 1
fi
