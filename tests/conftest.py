from pathlib import Path  # Use the modern pathlib instead

import pytest

# This line activates the sphinx testing plugin
pytest_plugins = "sphinx.testing.fixtures"


# This fixture provides the root directory of the project
@pytest.fixture(scope="session")
def rootdir() -> Path:
    return Path(__file__).parent.parent.absolute()


def pytest_addoption(parser):
    """Registers the 'sphinx_srcdir' option for pytest.ini."""
    parser.addini("sphinx_srcdir", "Sphinx source directory for tests", type="string", default=".")
