#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running Mandrel CI integration tests..."
if command -v uv >/dev/null 2>&1; then
  uv run --with pyyaml python "$SCRIPT_DIR/test-integrations.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/test-integrations.py" "$@"
else
  echo "ERROR: python3 or uv is required to run test-integrations"
  exit 1
fi
