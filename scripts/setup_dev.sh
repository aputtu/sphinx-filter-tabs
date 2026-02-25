#!/bin/bash
set -e

# --- Check for Python 3.12 and install if missing ---
echo "🐍 Checking for Python 3.12..."
if ! command -v python3.12 &> /dev/null
then
    echo "Python 3.12 not found. Installing via deadsnakes PPA..."
    echo "You may be prompted for your password to run 'sudo'."
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install python3.12 python3.12-venv -y
    echo "✅ Python 3.12 installed."
else
    echo "✅ Python 3.12 is already installed."
fi
echo ""

echo "🧹 Starting a full clean-up..."
# Remove virtual environment and tox cache directories
rm -rf venv
rm -rf .tox

# Remove Python bytecode cache directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove package build artifacts from setuptools/pip
rm -rf build dist *.egg-info

# Remove other testing artifacts
rm -rf .pytest_cache .coverage htmlcov

echo "✅ Clean-up complete."
echo ""
echo "Setting up sphinx-filter-tabs development environment..."

# Create and activate a virtual environment
python3.12 -m venv venv
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
echo "   make test       # Run tests"
echo "   make html       # Build HTML docs"
echo "   make pdf        # Build PDF docs"
echo "   make all        # Run tests + build all docs"
echo "   make clean      # Remove build artifacts"
echo "   make export     # Export project to txt for LLMs to use"
echo "   make            # Show all available targets"
echo ""
