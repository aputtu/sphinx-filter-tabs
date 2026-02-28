# AI Agent Instructions for sphinx-filter-tabs

## 1. Virtual Environments
Always prioritize using the virtual environment when running Python tools. The virtual environment is located in the `venv/` directory. If you try to run tools directly without activating it, you will get import errors and missing command errors. To execute commands reliably, prepend `venv/bin/` to the command (e.g., `venv/bin/pytest`, `venv/bin/ruff`).

## 2. Pytest Configuration
We fixed a historical issue where `pytest` would scan `venv/` infinitely by setting `testpaths` and `norecursedirs` inside `pytest.ini`. You can now safely run `venv/bin/pytest` from the root, but do not override these settings recursively without testing.

## 3. Tox Environments
Do not guess the names of `tox` environments (e.g., do not randomly run `tox -e ruff` or `tox -e type`). Always read `tox.ini` first to find the strictly defined environment names (e.g., `lint`, `mypy`) before attempting static analysis.

## 4. Strict Typing and Exports
The project enforces strict `mypy` checks. When modifying module entry points like `filter_tabs/__init__.py`, you must explicitly declare exported variables and functions in the `__all__` array. Failing to do so will cause `mypy` to fail the continuous integration build.

## 5. Architectural Structure
Be aware that the Sphinx extension is a modular package. A historically massive monolith file (`filter_tabs/extension.py`) was deleted and broken into tightly scoped modules (`nodes.py`, `directives.py`, `render_html.py`, etc.). Always start by reading `filter_tabs/__init__.py` to understand the tree structure, and do not attempt to recreate a single-file extension.

## 6. CSS Generation
Custom CSS is written dynamically to Sphinx's output `_static/` folder upon the `build-finished` event via `write_theme_css` in `filter_tabs/assets.py`. Do not manually create or edit static CSS files in the root folder hoping they will bundle; modify the Python writing logic instead.

## 7. Deferred Node Transformations
Do not attempt to replace or render nodes inside the `Directive.run()` methods. The core logic of merging, collapsing, and validating tabs happens during Sphinx's `doctree-resolved` event via `process_filter_tabs_nodes` in `transforms.py`.

## 8. Non-HTML Fallbacks
The extension supports non-HTML builders (like PDF via LaTeX) by detecting the builder format during `doctree-resolved` and running `render_fallback` (from `render_fallback.py`). This converts complex interactive tabs into flat, visible text admonitions. Always check if modifications to tabs affect this fallback logic.

## 9. Development Scripts
The repository contains a highly useful script at `scripts/dev.sh`. Instead of manually clearing Sphinx caches and recreating output logs, leverage `./scripts/dev.sh html` to build documentation or `./scripts/dev.sh clean-all` for a fresh rebuild.

## 10. HTML Assertions in Tests
The test suite aggressively verifies the underlying output structure using BeautifulSoup to parse Sphinx builds. If you change CSS class names or node nesting order in `render_html.py`, prepare to update multiple assertions in the `tests/` directory accordingly.

## 11. Test-Driven Development (TDD)
Whenever reasonable, adopt a Test-Driven Development (TDD) approach. Write or update tests in the `tests/` directory to define expected behavior before implementing new features or fixing bugs.

## 12. Ranked Historical Struggles
To save time, here are the top 5 issues previous AI agents struggled with the most in this codebase, ranked by severity:
1. **Pytest Infinite Hang:** Running a raw `pytest` command without targeting `tests/` caused infinite hangs scanning the massive `venv/` directory before `pytest.ini` was properly patched. Always use `venv/bin/pytest tests/`.
2. **Mypy Strictness on `__init__.py` Exports:** Breaking monolithic files into modules caused aggressive `mypy` failures because `__all__` wasn't explicitly declaring exports like `__version__`. Sphinx extensions require precise namespace exports.
3. **Guessing Tox Environments:** Assuming standard tox environment names (e.g., `ruff`, `type`) caused instant failures. The environments are strictly named `lint` and `mypy` in `tox.ini`.
4. **Operating Outside the Virtual Environment:** Failing to prepend `venv/bin/` to commands (`pip`, `pytest`, `ruff`) caused massive "command not found" or "module not found" confusion. 
5. **Docutils `deepcopy()` Bugs:** Attempting to `node.deepcopy()` docutils elements (like collapsing admonitions) destroyed node identities and broke downstream transforms. Nodes must be cleanly *moved*, not deepcopied.

## 13. Version Release Protocol
When incrementing the project version, you MUST enforce the following strict checklist:
1. **Changelog**: Append an appropriate entry documenting the changes to `CHANGELOG.md` (or equivalent changelog file).
2. **Code Constants**: The hardcoded version numbering MUST be updated synchronously across the following files:
   - `pyproject.toml` (update `version = "X.Y.Z"`)
   - `filter_tabs/__init__.py` (update `__version__ = "X.Y.Z"`)
## 14. Self-Documenting Architecture
The `sphinx-filter-tabs` project contains its own comprehensive documentation inside the `docs/` directory (`index.rst`, `usage.rst`, etc.). These files serve as the live examples and technical reference for the extension.
If you modify the codebase to add a new feature, change directive syntax, or alter existing behavior, you MUST synchronously update the appropriate `.rst` files in the `docs/` directory so the project accurately documents itself. Let the documentation be the ultimate source of truth.

## 15. Read Terminal Outputs Carefully
Do not run test or build commands asynchronously without explicitly reading their full terminal output. When `pytest` or `sphinx-build` fails, the stack trace contains the exact missing module or syntax error (e.g., dynamically generated test configurations failing to import a deleted module). Read the output directly rather than guessing with tools like `grep` first.
