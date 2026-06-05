#!/bin/sh
set -e

echo "Building documentation with Sphinx..."

# Build HTML
.venv/bin/sphinx-build -b html docs/ docs/_build/html

echo ""
echo "Documentation built successfully!"
echo "Open docs/_build/html/index.html in your browser"
