from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


def write_index(app: SphinxTestApp, content: str) -> None:
    app.srcdir.joinpath("index.rst").write_text(content, encoding="utf-8")


def build_index(app: SphinxTestApp, content: str) -> None:
    write_index(app, content)
    app.build()


def tab_group_rst(count: int, default_index: int = 0) -> str:
    tabs = "\n".join(
        f"    .. tab:: Tab {i}{' (default)' if i == default_index else ''}\n\n"
        f"        Content {i}.\n"
        for i in range(count)
    )
    return f"""
Test Document
=============

.. filter-tabs::

{tabs}
"""


def html_text(app: SphinxTestApp) -> str:
    return (app.outdir / "index.html").read_text(encoding="utf-8")


def html_soup(app: SphinxTestApp) -> BeautifulSoup:
    return BeautifulSoup(html_text(app), "html.parser")


def read_theme_css(app: SphinxTestApp) -> str:
    theme_css_path = app.outdir / "_static" / "filter_tabs_theme.css"
    assert theme_css_path.exists(), "filter_tabs_theme.css should be generated in _static/"
    return theme_css_path.read_text(encoding="utf-8")


def warning_text(app: SphinxTestApp) -> str:
    return app._warning.getvalue()


def project_root() -> Path:
    return Path(__file__).parent.parent.absolute()
