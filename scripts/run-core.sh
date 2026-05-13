#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Usage: ./scripts/run-core.sh [core arguments...]

Examples:
  ./scripts/run-core.sh
  ./scripts/run-core.sh --no-web --port 9000
  MCUB_NO_WEB=1 ./scripts/run-core.sh --core zen
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

exec python3 -m core "$@"
