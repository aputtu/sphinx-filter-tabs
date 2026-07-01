from __future__ import annotations


def test_docs_use_sphinx_default_html_theme(rootdir):
    """Docs should not carry theme-specific RTD template/config overrides."""
    conf = rootdir.joinpath("docs", "conf.py").read_text(encoding="utf-8")
    footer = rootdir.joinpath("docs", "_templates", "footer.html")

    assert 'html_theme = "sphinx_rtd_theme"' not in conf
    assert '"sphinx_rtd_theme"' not in conf
    assert not footer.exists()


def test_docs_sidebar_template_keeps_visible_home_link(rootdir):
    """Section pages need an obvious route back to the docs landing page."""
    about = rootdir.joinpath("docs", "_templates", "about.html").read_text(encoding="utf-8")

    assert "sft-sidebar-home" in about
    assert "pathto(root_doc)" in about
    assert "Home" in about
