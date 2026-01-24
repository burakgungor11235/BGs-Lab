#!/bin/bash
# Build script for BGs Lab
# Generates OG images and builds the site with Zola

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

preview() {
	echo "Generating OG images..."
	python3 "$SCRIPT_DIR/scripts/generate_og.py"

	echo ""
	echo "Starting preview server at http://localhost:8787 ..."
	zola build --base-url http://localhost:8787
	cd worker
	npm run dev
}

build() {
	echo "Generating OG images..."
	python3 "$SCRIPT_DIR/scripts/generate_og.py"

	echo ""
	echo "Building site with Zola for production (https://bgslabs.org)..."
	zola build --base-url https://bgslabs.org

	echo ""
	echo "Build complete! Output in public/"
}

case "${1:-build}" in
preview)
	preview
	;;
build | deploy | *)
	build
	;;
esac
