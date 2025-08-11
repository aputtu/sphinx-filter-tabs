import pytest
from pathlib import Path  # Use the modern pathlib instead

# This line activates the sphinx testing plugin
pytest_plugins = "sphinx.testing.fixtures"

# This fixture provides the root directory of the project
@pytest.fixture(scope="session")
def rootdir() -> Path:
    return Path(__file__).parent.parent.absolute()