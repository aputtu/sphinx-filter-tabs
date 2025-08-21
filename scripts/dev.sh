#!/bin/bash
# dev.sh - Enhanced development commands with PDF support

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Install the package in development mode
install_package() {
    print_status "Installing package in development mode..."
    pip install -e . || {
        print_error "Failed to install package"
        exit 1
    }
    print_success "Package installed"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    pytest || {
        print_error "Tests failed"
        exit 1
    }
    print_success "All tests passed"
}

# Build HTML documentation
build_html() {
    print_status "Building HTML documentation..."
    sphinx-build -b html docs docs/_build/html || {
        print_error "HTML build failed"
        exit 1
    }
    print_success "HTML documentation built"
    print_status "HTML docs available at: docs/_build/html/index.html"
}

# Build PDF documentation
build_pdf() {
    print_status "Building PDF documentation..."
    
    # Step 1: Build LaTeX source
    print_status "Building LaTeX source files..."
    sphinx-build -b latex docs docs/_build/latex || {
        print_error "LaTeX build failed"
        exit 1
    }
    
    # Step 2: Compile LaTeX to PDF
    print_status "Compiling PDF from LaTeX..."
    (cd docs/_build/latex && make) || {
        print_error "PDF compilation failed"
        print_warning "Make sure you have LaTeX installed (texlive-latex-recommended)"
        exit 1
    }
    
    # Step 3: Copy PDF to downloads directory
    print_status "Copying PDF to downloads directory..."
    mkdir -p docs/_downloads
    cp docs/_build/latex/*.pdf docs/_downloads/ || {
        print_warning "Could not copy PDF to downloads directory"
    }
    
    print_success "PDF documentation built"
    print_status "PDF available at: docs/_build/latex/sphinxextension-filtertabs.pdf"
}

# Clean build directories
clean_build() {
    print_status "Cleaning build directories..."
    rm -rf docs/_build
    rm -rf build
    rm -rf dist
    rm -rf *.egg-info
    print_success "Build directories cleaned"
}

# Watch for changes and auto-rebuild
watch_changes() {
    print_status "Watching for changes... (Press Ctrl+C to stop)"
    
    # Check if watchdog is installed
    python -c "import watchdog" 2>/dev/null || {
        print_warning "watchdog not installed. Installing..."
        pip install watchdog
    }
    
    # Watch for Python and RST file changes
    watchmedo shell-command \
        --patterns="*.py;*.rst;*.css;*.js" \
        --recursive \
        --command="echo 'Files changed, rebuilding...' && pip install -e . && sphinx-build -b html docs docs/_build/html" \
        . &
    
    # Keep the script running
    wait
}

# Show help
show_help() {
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  test          Install package and run tests"
    echo "  html          Install package and build HTML docs"
    echo "  pdf           Install package and build PDF docs"
    echo "  docs          Install package and build both HTML and PDF docs"
    echo "  all           Install package, run tests, and build all docs"
    echo "  clean         Clean all build directories"
    echo "  clean-all     Clean build directories, then build everything"
    echo "  watch         Watch for file changes and auto-rebuild HTML"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh test                    # Quick test after code changes"
    echo "  ./dev.sh html                    # Build HTML docs"
    echo "  ./dev.sh pdf                     # Build PDF docs"
    echo "  ./dev.sh docs                    # Build both HTML and PDF"
    echo "  ./dev.sh all                     # Run tests and build everything"
    echo "  ./dev.sh clean-all               # Clean slate rebuild"
}

# Main command handling
case "$1" in
    "test")
        install_package
        run_tests
        ;;
    "html")
        install_package
        build_html
        ;;
    "pdf")
        install_package
        build_pdf
        ;;
    "docs")
        install_package
        build_html
        build_pdf
        ;;
    "all")
        install_package
        run_tests
        build_html
        build_pdf
        print_success "Everything completed successfully!"
        ;;
    "clean")
        clean_build
        ;;
    "clean-all")
        clean_build
        install_package
        run_tests
        build_html
        build_pdf
        print_success "Clean rebuild completed!"
        ;;
    "watch")
        install_package
        watch_changes
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        print_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

