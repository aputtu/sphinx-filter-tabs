#!/bin/bash
# cleanup_legacy.sh - Remove legacy dual implementation files

set -e

echo "🧹 Cleaning up legacy dual implementation files..."

# Files to remove completely
FILES_TO_REMOVE=(
    "filter_tabs/config.py"
    "filter_tabs/static/filter_tabs_legacy.css"
    "filter_tabs/static/filter_tabs_common.css"
    "filter_tabs/static/filter_tabs_accessible.css"
    "filter_tabs/static/filter_tabs.css"  # Will be replaced
    "setup_patch.py"
    "validate_dual_implementation.py"
    "tests/test_dual_implementation.py"
    "scripts/setup_dual_implementation.sh"
)

# Remove files
for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        echo "🗑️  Removing $file"
        rm "$file"
    else
        echo "⚠️  File $file not found (already removed?)"
    fi
done

echo "✅ Legacy files removed"

# Create new simplified CSS from the cleaned version
echo "📝 Creating new simplified filter_tabs.css..."
cat > "filter_tabs/static/filter_tabs.css" << 'EOF'
/* Sphinx Filter Tabs - Simplified Accessibility-First Stylesheet */

/* Main container */
.sft-container {
    border: 1px solid #e0e0e0;
    border-radius: var(--sft-border-radius, 8px);
    overflow: hidden;
    margin: 1.5em 0;
    background: white;
}

/* Semantic structure */
.sft-fieldset {
    border: none;
    padding: 0;
    margin: 0;
}

/* Visible, meaningful legend */
.sft-legend {
    background: #f8f9fa;
    padding: 12px 20px;
    margin: 0;
    font-weight: 600;
    color: #495057;
    border-bottom: 1px solid #e0e0e0;
    width: 100%;
    font-size: 0.95em;
}

/* Radio group container */
.sft-radio-group {
    display: flex;
    flex-wrap: wrap;
    background: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
    padding: 0 10px;
}

/* Hidden radio buttons (accessible to screen readers) */
.sft-radio-group input[type="radio"] {
    width: 1px;
    height: 1px;
    opacity: 0.01;
    position: absolute;
    z-index: -1;
    margin: 0;
}

/* Tab labels */
.sft-radio-group label {
    display: block;
    padding: 12px 18px;
    cursor: pointer;
    transition: all 0.2s ease;
    border-bottom: 3px solid transparent;
    color: #6c757d;
    font-weight: 500;
    font-size: var(--sft-tab-font-size, 1em);
    position: relative;
    background: transparent;
}

/* Active tab styling */
.sft-radio-group input[type="radio"]:checked + label {
    color: var(--sft-tab-highlight-color, #007bff);
    border-bottom-color: var(--sft-tab-highlight-color, #007bff);
    background: white;
    font-weight: 600;
}

/* Focus styling for keyboard navigation */
.sft-radio-group input[type="radio"]:focus + label {
    outline: 2px solid var(--sft-tab-highlight-color, #007bff);
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(0, 123, 255, 0.25);
    z-index: 1;
}

/* Hover effects */
.sft-radio-group label:hover {
    color: #495057;
    background: rgba(0, 123, 255, 0.05);
}

/* Content area */
.sft-content {
    padding: 20px;
}

/* Panels - hidden by default */
.sft-panel {
    display: none;
    outline: none;
}

/* Focus styling for panels */
.sft-panel:focus {
    outline: 2px solid var(--sft-tab-highlight-color, #007bff);
    outline-offset: -2px;
    border-radius: 4px;
}

/* General content panel - always visible */
.sft-panel[data-filter="General"] {
    display: block;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

/* Screen reader only content */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* Collapsible sections */
.collapsible-section {
    border: 1px solid #e0e0e0;
    border-left: 4px solid var(--sft-collapsible-accent-color, #17a2b8);
    border-radius: 4px;
    margin-top: 1em;
}

.collapsible-section summary {
    display: block;
    cursor: pointer;
    padding: 12px;
    font-weight: bold;
    background-color: #f9f9f9;
    outline: none;
    list-style: none;
}

.collapsible-section summary::-webkit-details-marker {
    display: none;
}

.collapsible-section[open] > summary { 
    border-bottom: 1px solid #e0e0e0; 
}

.custom-arrow { 
    display: inline-block; 
    width: 1em; 
    margin-right: 8px; 
    transition: transform 0.2s; 
}

.collapsible-section[open] > summary .custom-arrow { 
    transform: rotate(90deg); 
}

.collapsible-content { 
    padding: 15px; 
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .sft-radio-group input[type="radio"]:checked + label {
        border-bottom-width: 4px;
    }
    
    .sft-radio-group input[type="radio"]:focus + label {
        box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.8);
    }
}

/* Reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
    .sft-radio-group label,
    .custom-arrow {
        transition: none;
    }
}
EOF

echo "✅ New simplified CSS created"

# Update version in pyproject.toml to indicate breaking change
echo "📝 Updating version to 2.0.0 in pyproject.toml..."
if [ -f "pyproject.toml" ]; then
    sed -i 's/version = "1\.0\.0"/version = "2.0.0"/' pyproject.toml
    echo "✅ Version updated to 2.0.0"
else
    echo "⚠️  pyproject.toml not found"
fi

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "📋 Summary of changes:"
echo "  ✅ Removed dual implementation system"
echo "  ✅ Removed legacy CSS files" 
echo "  ✅ Created simplified filter_tabs.css"
echo "  ✅ Bumped version to 2.0.0 (breaking change)"
echo ""
echo "📝 Next steps:"
echo "  1. Replace filter_tabs/extension.py with the cleaned version"
echo "  2. Replace filter_tabs/renderer.py with the cleaned version" 
echo "  3. Replace tests/test_extension.py with the cleaned version"
echo "  4. Remove tests/test_accessibility_compliance.py (if no longer needed)"
echo "  5. Update documentation to remove dual implementation references"
echo "  6. Test the simplified implementation"
echo ""
echo "⚠️  This is a BREAKING CHANGE - bump to version 2.0.0"
