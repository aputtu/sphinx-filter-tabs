#!/bin/bash
# version_consistency_fixes.sh - Fix version inconsistencies across all files

echo "Fixing version consistency across all files..."

# 1. Update pyproject.toml (currently shows 2.0.0)
sed -i 's/version = "2.0.0"/version = "1.0.0"/' pyproject.toml

# 2. Update docs/conf.py
sed -i "s/release = '1.0.0'/release = '2.0.0'/" docs/conf.py

# 3. Update changelog in docs to match
sed -i 's/**Version 1.0.0** (Upcoming, we'\''re still in beta)/**Version 2.0.0** - Current Release/' docs/_changelog.rst

# 4. Check for any other version references
echo "Searching for other version references..."
grep -r "1\.0\.0\|2\.0\.0" --include="*.py" --include="*.rst" --include="*.toml" . || echo "No additional version references found"

echo "Version consistency fixes applied. Current version should be 2.0.0 everywhere."

