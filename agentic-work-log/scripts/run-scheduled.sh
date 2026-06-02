#!/usr/bin/env bash
# Scheduled runner for agentic-work-log — requires AGENTIC_WORK_LOG_NOTE_ID or config.
set -euo pipefail

LOG_DIR="${AGENTIC_WORK_LOG_LOG_DIR:-$HOME/.config/agentic-work-log/logs}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y-%m-%d).log"
PROMPT='/agentic-work-log'

if [[ -z "${AGENTIC_WORK_LOG_NOTE_ID:-}" ]] && [[ ! -f "$HOME/.config/agentic-work-log/config.json" ]]; then
  echo "agentic-work-log: set AGENTIC_WORK_LOG_NOTE_ID or ~/.config/agentic-work-log/config.json" >>"$LOG"
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

if [[ -n "${AGENTIC_WORK_LOG_RUNNER:-}" ]]; then
  "run_${AGENTIC_WORK_LOG_RUNNER}"
else
  run_cursor || run_claude || run_codex || run_opencode
fi
