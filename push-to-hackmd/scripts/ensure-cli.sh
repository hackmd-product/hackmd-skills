#!/usr/bin/env bash
# Verify hackmd-cli is on PATH; install @hackmd/hackmd-cli when INSTALL=1.
set -euo pipefail

if command -v hackmd-cli >/dev/null 2>&1; then
  hackmd-cli version
  exit 0
fi

echo "hackmd-cli not found." >&2
echo "Install: npm install -g @hackmd/hackmd-cli" >&2
echo "Docs: https://github.com/hackmdio/hackmd-cli" >&2

if [[ "${INSTALL:-0}" == "1" ]]; then
  npm install -g @hackmd/hackmd-cli
  hackmd-cli version
  exit 0
fi

exit 1
