#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DOCS_DIR/.." && pwd)"
SRC_DIR="$ROOT_DIR/src"
PKG_NAME="x_logger"

export PYTHONPATH="$SRC_DIR:${PYTHONPATH:-}"
rm -rf "$DOCS_DIR/_build"
mkdir -p "$DOCS_DIR/_build/html"

for LANG_CODE in en ja; do
    LANG_DIR="$DOCS_DIR/$LANG_CODE"
    mkdir -p "$LANG_DIR/api"
    rm -f "$LANG_DIR/api"/*.rst
    sphinx-apidoc -o "$LANG_DIR/api" "$SRC_DIR/$PKG_NAME" -f --module-first
    export SPHINX_LANGUAGE="$LANG_CODE"
    sphinx-build -b html -c "$DOCS_DIR" "$LANG_DIR" "$DOCS_DIR/_build/html/$LANG_CODE"
done

cp -a "$DOCS_DIR/_build/html/en/." "$DOCS_DIR/_build/html/"
touch "$DOCS_DIR/_build/html/.nojekyll"
