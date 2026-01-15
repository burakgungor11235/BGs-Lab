#!/bin/bash
# Build script for BG's Blog
# Generates OG images and builds the site with Zola

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Generating OG images..."
python3 "$SCRIPT_DIR/scripts/generate_og.py"

echo ""
echo "Building site with Zola..."
zola build

echo ""
echo "Build complete! Output in public/"
