#!/bin/bash
set -e

echo "🧹 Starting a full clean-up..."
# Remove the virtual environment to ensure fresh dependencies
rm -rf venv

# Remove Python bytecode cache directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove package build artifacts from setuptools/pip
rm -rf build dist *.egg-info

# Remove testing artifacts
rm -rf .pytest_cache .coverage htmlcov

echo "✅ Clean-up complete."
echo ""
echo "Setting up sphinx-filter-tabs development environment..."

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements/dev.txt
pip install -r requirements/docs.txt
pip install -e .

# Remove the Sphinx build cache specifically before building
rm -rf docs/_build

echo "Building HTML documentation..."
sphinx-build -b html docs docs/_build/html

echo "Building LaTeX source files..."
sphinx-build -b latex docs docs/_build/latex

# --- NEW: Compile the LaTeX source into a PDF ---
echo "Compiling PDF from LaTeX..."
# Use the Makefile provided by Sphinx to run the pdflatex compiler
(cd docs/_build/latex && make)

echo ""
echo "✅ Development environment ready!"
echo "To activate it in your terminal, run: source venv/bin/activate"
