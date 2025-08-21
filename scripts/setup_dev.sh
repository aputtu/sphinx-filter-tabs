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

echo "✅ Development environment ready!"
echo ""

# Make all development scripts executable
echo "📋 Making development scripts executable..."
find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# List the scripts that were made executable
if [ -d "scripts" ]; then
    echo "✅ Made executable:"
    find scripts/ -name "*.sh" -executable -exec echo "   📄 {}" \;
fi

echo ""
echo "--- Starting Documentation Build ---"

# 1. Build LaTeX source files first
echo "Building LaTeX source files..."
sphinx-build -b latex docs docs/_build/latex

# 2. Compile the LaTeX source into a PDF which HTML will refer to
echo "Compiling PDF from LaTeX..."
(cd docs/_build/latex && make)

# 3. Copy the generated PDF into the source tree for linking
echo "Copying PDF to downloads directory..."
# Use a wildcard (*) to be safe against small name changes
cp docs/_build/latex/*.pdf docs/_downloads/

# 4. NOW, build the HTML documentation
echo "Building HTML documentation..."
sphinx-build -b html docs docs/_build/html

echo ""
echo "✅ Build complete!"
echo ""
echo "📋 Available commands:"
echo "   source venv/bin/activate     # Activate virtual environment"
echo "   ./scripts/dev.sh test        # Run tests"
echo "   ./scripts/dev.sh html        # Build HTML docs"
echo "   ./scripts/dev.sh all         # Run tests + build docs"
echo "   ./scripts/export-project.sh  # Export complete project to txt for LLMs to use"
echo ""