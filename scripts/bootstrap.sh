#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
  cat <<'EOF'
Usage: ./scripts/bootstrap.sh

Creates virtualenv and installs runtime + dev dependencies.

Env:
  VENV_DIR   Virtualenv path (default: .venv)
  PYTHON_BIN Python binary (default: python3)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

echo "Using python: $PYTHON_BIN"
$PYTHON_BIN --version

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtualenv: $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ -f tests/requirements-dev.txt ]]; then
  python -m pip install -r tests/requirements-dev.txt
fi

echo "Bootstrap complete."
echo "Activate with: source $VENV_DIR/bin/activate"
