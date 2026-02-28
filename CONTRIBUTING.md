# Contributing to sphinx-filter-tabs

Thank you for your interest in contributing to `sphinx-filter-tabs`! This document provides guidelines for setting up your development environment and submitting changes.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aputtu/sphinx-filter-tabs.git
   cd sphinx-filter-tabs
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Workflow

### Running Tests
We use `pytest` for testing. Always run tests from the root directory using the virtual environment's executable to avoid path issues:
```bash
venv/bin/pytest tests/
```

### Static Analysis
We enforce strict typing and linting:
- **Linting**: We use `ruff` for formatting and linting.
  ```bash
  venv/bin/ruff check filter_tabs/ tests/
  venv/bin/ruff format filter_tabs/ tests/
  ```
- **Type Checking**: We use `mypy`.
  ```bash
  venv/bin/mypy filter_tabs/
  ```

### Sphinx Documentation
To build and view the project's own documentation:
```bash
./scripts/dev.sh html
```

## Pull Request Guidelines

1. **Create a Branch**: Use a descriptive name like `fix/issue-description` or `feat/new-feature`.
2. **Follow Pythonic Best Practices**: Adhere to PEP 8, use modern type hints, and write idiomatic code.
3. **Update Documentation**: If you change behavior or add features, update the files in `docs/`.
4. **Pass all checks**: Ensure `pytest`, `ruff`, and `mypy` all pass before submitting.
5. **Sync Versioning**: If your change warrants a version bump, update `pyproject.toml` and `filter_tabs/__init__.py`.
