#!/usr/bin/env bash
# Sphinx ドキュメントをクリーン＆ビルドするスクリプト

set -euo pipefail

# SPHINX_SRC="sphinx_docs"
SPHINX_SRC="."
SPHINX_BUILD_DIR="$SPHINX_SRC/_build"
SPHINX_OUT="$SPHINX_BUILD_DIR/html"
SPHINX_SOURCE_DIR="$SPHINX_SRC/source"
# SRC="src/x_logger"
SRC="../src/x_logger"

echo "Cleaning build & source directories..."
rm -rf "$SPHINX_BUILD_DIR"
rm -rf "$SPHINX_SOURCE_DIR"

echo "Regenerating .rst files with sphinx-apidoc..."
sphinx-apidoc -f -o "$SPHINX_SOURCE_DIR" "$SRC"

mkdir -p "$SPHINX_SRC/_static"
mkdir -p "$SPHINX_SRC/locales/ja/LC_MESSAGES"

echo "Building Sphinx docs..."
sphinx-build -b html -W -n -T -v "$SPHINX_SRC" "$SPHINX_OUT"

echo "Build finished. Open the result with:"
echo "open \"$SPHINX_OUT/index.html\""