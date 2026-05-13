#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Usage: ./scripts/check.sh [--fix]

Runs:
  1) Hidden/invisible unicode checks
  2) Ruff lint
  3) Pytest

Options:
  --fix  Enable auto-fix where possible:
         - hidden-characters-detector: --clean --yes
         - ruff: --fix
EOF
}

FIX_MODE=0
if [[ "${1:-}" == "--fix" ]]; then
  FIX_MODE=1
  shift
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

run_hidden_chars_check() {
  echo "[check] hidden chars"
  local has_detector=0

  if command -v hidden-characters-detector >/dev/null 2>&1; then
    has_detector=1
    detector_args=(-d .)
    if [[ "$FIX_MODE" -eq 1 ]]; then
      detector_args+=(--clean --yes)
    fi
    detector_args+=(
      --ignore-dir .git \
      --ignore-dir .venv \
      --ignore-dir __pycache__ \
      --ignore-dir modules_loaded
    )

    if hidden-characters-detector "${detector_args[@]}"; then
      return
    fi
    echo "TIP: hidden-characters-detector failed; using built-in fallback scanner."
  fi

  if [[ "$has_detector" -eq 0 ]]; then
    echo "TIP: 'hidden-characters-detector' is not installed."
    echo "TIP: install it with: ./scripts/install-hidden-characters-detector.sh"
  fi

  # Fallback scanner: catches bidi controls and most invisible format chars.
  python3 - <<'PY'
from __future__ import annotations

import pathlib
import sys
import unicodedata

ROOT = pathlib.Path(".")
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "modules_loaded",
}
EXTENSIONS = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".sh"}

BIDI_CONTROLS = {
    "\u202A", "\u202B", "\u202C", "\u202D", "\u202E",
    "\u2066", "\u2067", "\u2068", "\u2069",
}
ALLOWED = {"\n", "\r", "\t"}

def should_scan(path: pathlib.Path) -> bool:
    if path.suffix not in EXTENSIONS:
        return False
    for part in path.parts:
        if part in EXCLUDED_DIRS:
            return False
    return True

def suspicious(char: str) -> bool:
    if char in ALLOWED:
        return False
    category = unicodedata.category(char)
    if char in BIDI_CONTROLS:
        return True
    if category == "Cf":
        return True
    if category == "Cc":
        return True
    return False

issues: list[tuple[str, int, int, str, str]] = []
for path in ROOT.rglob("*"):
    if not path.is_file() or not should_scan(path):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    line = 1
    col = 0
    for ch in text:
        if ch == "\n":
            line += 1
            col = 0
            continue
        col += 1
        if suspicious(ch):
            issues.append(
                (
                    str(path),
                    line,
                    col,
                    f"U+{ord(ch):04X}",
                    unicodedata.name(ch, "UNKNOWN"),
                )
            )

if issues:
    for file_path, line, col, codepoint, name in issues:
        print(f"{file_path}:{line}:{col}: {codepoint} {name}")
    sys.exit(1)

print("No suspicious hidden/control unicode characters found.")
PY
}

run_hidden_chars_check

echo "[check] ruff"
if [[ "$FIX_MODE" -eq 1 ]]; then
  python3 -m ruff check --fix .
else
  python3 -m ruff check .
fi

echo "[check] pytest"
python3 -m pytest
