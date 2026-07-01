from __future__ import annotations


def test_docs_use_sphinx_default_html_theme(rootdir):
    """Docs should not carry theme-specific RTD template/config overrides."""
    conf = rootdir.joinpath("docs", "conf.py").read_text(encoding="utf-8")
    footer = rootdir.joinpath("docs", "_templates", "footer.html")

    assert 'html_theme = "sphinx_rtd_theme"' not in conf
    assert '"sphinx_rtd_theme"' not in conf
    assert not footer.exists()
