Release Checklist
=================

Use this checklist before tagging a release.

1. Update the package version in ``pyproject.toml`` and
   ``filter_tabs/__init__.py``.
2. Add a dated entry to ``docs/changelog.rst`` with the user-visible changes,
   compatibility notes, and any security-relevant dependency updates.
3. Run the local quality gates:

   .. code-block:: bash

      ruff check filter_tabs tests docs/_ext scripts/validate_docs.py
      ruff format --check filter_tabs tests docs/_ext scripts/validate_docs.py
      mypy filter_tabs/
      pytest

4. Build and validate the HTML documentation:

   .. code-block:: bash

      sphinx-build -E -a -b html docs docs/_build/html
      python scripts/validate_docs.py docs/_build/html

5. Rebuild the PDF download and then rebuild HTML so the download link points
   to the fresh PDF:

   .. code-block:: bash

      ./scripts/dev.sh docs

6. Confirm ``docs/_build/html`` contains the expected rendered examples and
   that the PDF includes the PDF-only fallback notice.
7. Create a focused release commit, tag it as ``vX.Y.Z``, and push the tag.
8. Verify that GitHub Actions finishes the test matrix, documentation
   validation, Pages deployment, and PyPI publish job.
