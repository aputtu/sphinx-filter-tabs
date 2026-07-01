from pathlib import Path

import pytest

from tests.helpers import project_root

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(scope="session")
def rootdir() -> Path:
    return project_root()


def pytest_addoption(parser):
    """Registers the 'sphinx_srcdir' option for pytest.ini."""
    parser.addini("sphinx_srcdir", "Sphinx source directory for tests", type="string", default=".")
