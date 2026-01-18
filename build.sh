#!/bin/bash
# Build script for BGs Lab
# Generates OG images and builds the site with Zola

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Generating OG images..."
python3 "$SCRIPT_DIR/scripts/generate_og.py"

echo ""
echo "Building site with Zola..."
zola build

# Copy redirect.html to index.html at root for proper GitHub Pages redirect
cp "$SCRIPT_DIR/static/redirect.html" "$SCRIPT_DIR/public/index.html"

echo ""
echo "Build complete! Output in public/"
