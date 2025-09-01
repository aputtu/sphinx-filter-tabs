#!/bin/bash
# export-project.sh - Export complete project structure and contents

# Generate timestamp for filename
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_FILE="../sphinx-filtertabs-export_${TIMESTAMP}.txt"

echo "🔄 Exporting project to: $OUTPUT_FILE"

# Create the export file
{
    echo "# Sphinx Filter Tabs - Complete Project Export"
    echo "# Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "# Working Directory: $(pwd)"
    echo ""
    
    echo "================================================================================"
    echo "PROJECT STRUCTURE"
    echo "================================================================================"
    echo ""
    
    # Project tree structure, now ignoring dist and .pytest_cache
    tree -a -I '.git|.tox|venv|dist|.pytest_cache|*.egg-info|_build|__pycache__|*.pyc|*.pdf'
    
    echo ""
    echo ""
    echo "================================================================================"
    echo "FILE CONTENTS"
    echo "================================================================================"
    echo ""
    
    # Find and display file contents, now ignoring dist and .pytest_cache
    find . -type f \
        -not -path './.git/*' \
        -not -path './.tox/*' \
        -not -path './venv/*' \
        -not -path './dist/*' \
        -not -path './.pytest_cache/*' \
        -not -path './*/__pycache__/*' \
        -not -path './docs/_build/*' \
        -not -path './docs/_downloads/*.pdf' \
        -not -path './*.egg-info/*' \
        -not -name '*.pyc' \
        -not -name '*.pyo' \
        -not -name '.DS_Store' \
        -not -name 'Thumbs.db' \
        -exec sh -c '
            echo "=== $1 ==="
            if file "$1" | grep -q "text\|empty"; then
                cat "$1"
            else
                echo "[Binary file - content not displayed]"
            fi
            echo ""
        ' _ {} \;
    echo ""
    echo "================================================================================"
    echo "EXPORT COMPLETE"
    echo "================================================================================"
    # ... rest of the script ...

} > "$OUTPUT_FILE"

echo "✅ Export complete!"
echo "📁 File: $OUTPUT_FILE"
echo "📊 Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
