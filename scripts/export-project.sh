#!/bin/bash
# export-project.sh - Export complete project structure and contents
# Excludes artifacts, builds, virtual environments, and binary files.

# Generate timestamp for filename
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_FILE="../sphinx-filtertabs-export_${TIMESTAMP}.txt"

echo "🔄 Exporting project to: $OUTPUT_FILE"

# Define exclusion pattern for 'tree'
# Matches: .git, .tox, any venv/env variant, build artifacts, cache, IDE folders
TREE_IGNORE='.git|.tox|venv*|.venv*|env*|dist|build|*.egg-info|_build|__pycache__|*.pyc|*.pdf|htmlcov|.coverage|.pytest_cache|.vscode|.idea|.claude|.mypy_cache|.ruff_cache|test-root'

{
    echo "# Sphinx Filter Tabs - Complete Project Export"
    echo "# Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "# Working Directory: $(pwd)"
    echo ""

    echo "================================================================================"
    echo "PROJECT STRUCTURE"
    echo "================================================================================"
    echo ""

    # -a: All files (hidden included)
    # -I: Ignore pattern
    tree -a -I "$TREE_IGNORE"

    echo ""
    echo ""
    echo "================================================================================"
    echo "FILE CONTENTS"
    echo "================================================================================"
    echo ""

    # Find files, pruning ignored directories to prevent traversal
    find . \
        \( \
            -name ".git" -o \
            -name ".tox" -o \
            -name "venv*" -o \
            -name ".venv*" -o \
            -name "env*" -o \
            -name "dist" -o \
            -name "build" -o \
            -name ".log	" -o \
            -name "test_out.txt" -o \
            -name "*.egg-info" -o \
            -name "htmlcov" -o \
            -name "image*" -o \
            -name ".pytest_cache" -o \
            -name "__pycache__" -o \
            -name "_build" -o \
            -name ".vscode" -o \
            -name ".idea" -o \
            -name ".claude" -o \
            -name ".mypy_cache" -o \
            -name ".ruff_cache" -o \
            -name "test-root" \
        \) -prune -o \
        -type f \
        -not -name '*.pyc' \
        -not -name '*.pyo' \
        -not -name '*.pdf' \
        -not -name '*.log' \
        -not -name '.DS_Store' \
        -not -name 'Thumbs.db' \
        -not -name '.coverage' \
        -print0 | xargs -0 -I {} sh -c '
            echo "=== {} ==="
            if file "{}" | grep -q "text\|empty"; then
                cat "{}"
            else
                echo "[Binary file - content not displayed]"
            fi
            echo ""
        '

    echo ""
    echo "================================================================================"
    echo "EXPORT COMPLETE"
    echo "================================================================================"

} > "$OUTPUT_FILE"

echo "✅ Export complete!"
echo "📁 File: $OUTPUT_FILE"
echo "📊 Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
