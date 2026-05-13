#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install-hidden-characters-detector.sh

Downloads hidden-characters-detector zip, unpacks it, and installs into
the current Python environment as a standalone CLI.

Env:
  HCD_ZIP_URL  ZIP URL (default: https://x0.at/Qg8G.zip)
  HCD_INSTALL_DIR  Install directory for sources
                   (default: ~/.local/share/hidden-characters-detector)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

ZIP_URL="${HCD_ZIP_URL:-https://x0.at/Qg8G.zip}"
INSTALL_DIR="${HCD_INSTALL_DIR:-$HOME/.local/share/hidden-characters-detector}"
TMP_DIR="$(mktemp -d)"
ZIP_PATH="$TMP_DIR/hidden-characters-detector.zip"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Downloading: $ZIP_URL"
curl -fsSL "$ZIP_URL" -o "$ZIP_PATH"

echo "Unpacking archive..."
unzip -q "$ZIP_PATH" -d "$TMP_DIR"

SOURCE_DIR="$(find "$TMP_DIR" -maxdepth 2 -type f -name setup.py -printf '%h\n' | head -n 1)"
if [[ -z "$SOURCE_DIR" ]]; then
  echo "Could not find package source (setup.py) in archive." >&2
  exit 1
fi

SCRIPT_PATH="$SOURCE_DIR/hidden-characters-detector.py"
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "Could not find hidden-characters-detector.py in archive." >&2
  exit 1
fi

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_PATH" "$INSTALL_DIR/hidden-characters-detector.py"
chmod +x "$INSTALL_DIR/hidden-characters-detector.py"

PY_SCRIPTS_DIR="$(python3 -c 'import sysconfig; print(sysconfig.get_path("scripts"))')"
mkdir -p "$PY_SCRIPTS_DIR"

LAUNCHER="$PY_SCRIPTS_DIR/hidden-characters-detector"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/hidden-characters-detector.py" "\$@"
EOF
chmod +x "$LAUNCHER"

echo "Installed. Verify with:"
echo "  hidden-characters-detector --version"
echo "Installed launcher:"
echo "  $LAUNCHER"
