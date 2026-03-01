#!/usr/bin/env bash
# Build WOLKE binary with PyInstaller. Run from repo root: ./scripts/build_exe.sh
# Requires: uv (https://docs.astral.sh/uv/)
set -e
cd "$(dirname "$0")/.."
if [ ! -f "wolke/__init__.py" ]; then
  echo "Error: Run from repo root. wolke package not found."
  exit 1
fi
uv sync --extra dev
uv run pyinstaller wolke.spec
echo ""
echo "If successful: dist/WOLKE (or dist/WOLKE.exe on Windows)"
echo "Run it; browser will open. config.ini next to binary or set WOLKE_CONFIG."
