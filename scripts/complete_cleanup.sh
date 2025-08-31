#!/bin/bash
# complete_cleanup.sh - Remove all legacy references and dual implementation code

echo "Starting complete cleanup of legacy references..."

# 1. Remove files that reference dual implementations
echo "Removing dual implementation files..."
rm -f scripts/dev_validation.sh  # References dual implementation testing
rm -f scripts/cleanup_legacy.sh  # Already completed, no longer needed
rm -f scripts/integrate_refactoring.py  # Refactoring integration is done

# 2. Clean up extension.py comments and remove unused code
echo "Cleaning extension.py..."
# Remove any comments about dual implementation
sed -i '/dual implementation/I d' filter_tabs/extension.py
sed -i '/legacy/I d' filter_tabs/extension.py

# 3. Remove unused configuration options from documentation
echo "Updating documentation..."
# Update installation docs to remove excessive config options
cat > docs/_installation.rst << 'EOF'
Installation
============

Installing the Package
----------------------

First, install the extension package using pip:

.. code-block:: bash

   pip install sphinx-filter-tabs

Or if you're using conda:

.. code-block:: bash

   conda install -c conda-forge sphinx-filter-tabs

Enabling the Extension
----------------------

After installation, you must enable the extension in your Sphinx project's 
``conf.py`` file. Add ``'filter_tabs.extension'`` to your ``extensions`` list:

.. code-block:: python

   # conf.py
   extensions = [
       # ... your other extensions ...
       'filter_tabs.extension',
   ]

Optional Configuration
----------------------

You can customize the extension with these optional settings in your ``conf.py``:

.. code-block:: python

   # Essential theming
   filter_tabs_highlight_color = '#007bff'  # Active tab highlight color
   
   # Development option
   filter_tabs_debug_mode = False           # Enable debug logging

That's it! The extension uses sensible defaults for everything else.

Verifying Installation
----------------------

To verify the extension is properly installed and loaded:

1. Build your documentation:

   .. code-block:: bash

      sphinx-build -b html docs docs/_build/html

2. Check for any errors in the output. If the extension loads correctly, 
   you should see no warnings about ``filter_tabs``.

3. Try using the directive in an RST file:

   .. code-block:: rst

      .. filter-tabs::

          .. tab:: Test

              If you see this, it works!
EOF

# 4. Update scripts/dev.sh to remove obsolete options
echo "Simplifying dev.sh..."
sed -i '/dual/I d' scripts/dev.sh
sed -i '/legacy/I d' scripts/dev.sh

# 5. Clean up test files
echo "Removing obsolete test references..."
# Remove any test files that reference dual implementations
find tests/ -name "*.py" -exec grep -l "dual\|legacy" {} \; | while read file; do
    echo "Found dual/legacy references in: $file"
    sed -i '/dual/I d' "$file"
    sed -i '/legacy/I d' "$file"
done

# 6. Update README.md to reflect simplified approach
echo "Updating README.md..."
sed -i 's/robust, accessible, and JavaScript-free/simple, accessible, and JavaScript-free/' README.md

# 7. Remove any .old or _old backup files created during refactoring
echo "Removing backup files..."
find . -name "*.old" -o -name "*_old.py" -o -name "*_old.*" | while read file; do
    echo "Removing backup file: $file"
    rm "$file"
done

echo "Cleanup complete!"
echo ""
echo "Summary of changes:"
echo "  - Removed dual implementation scripts and references"
echo "  - Simplified documentation configuration section"
echo "  - Cleaned up comments in code files"
echo "  - Removed backup files from refactoring"
echo "  - Updated README to reflect simplified approach"
echo ""
echo "Your extension is now clean and simplified!"

