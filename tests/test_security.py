# tests/test_security.py

import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp


@pytest.mark.sphinx("html")
def test_xss_in_tab_name(app: SphinxTestApp):
    """Verify that malicious tab names are properly escaped to prevent XSS."""
    xss_payload = '<script>alert("xss")</script>'
    content = f"""
Test XSS
========

.. filter-tabs::

    .. tab:: {xss_payload}

        Content
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    html_content = (app.outdir / "index.html").read_text()

    # Check if the raw payload exists in the HTML
    assert xss_payload not in html_content, "XSS payload found unescaped in HTML!"

    # Check if it's escaped
    soup = BeautifulSoup(html_content, "html.parser")
    label = soup.select_one(".sft-radio-group label")
    assert label.text.strip() == xss_payload, (
        "Tab name should match payload textually but be escaped in HTML"
    )


@pytest.mark.sphinx("html")
def test_xss_in_legend(app: SphinxTestApp):
    """Verify that malicious legend options are properly escaped to prevent XSS."""
    xss_payload = "<img src=x onerror=alert(1)>"
    content = f"""
Test XSS Legend
===============

.. filter-tabs::
   :legend: {xss_payload}

   .. tab:: Python
      Content
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    html_content = (app.outdir / "index.html").read_text()

    # Check if the raw payload exists in the HTML
    assert xss_payload not in html_content, "XSS payload (legend) found unescaped in HTML!"

    soup = BeautifulSoup(html_content, "html.parser")
    legend = soup.select_one(".sft-legend")
    assert legend.text.strip() == xss_payload, (
        "Legend text should match payload textually but be escaped in HTML"
    )


@pytest.mark.sphinx("html")
def test_css_injection_in_highlight_color(app: SphinxTestApp):
    """Verify that malicious highlight color configuration doesn't lead to CSS injection."""
    # This payload tries to close the :root block and start a new one
    css_payload = 'red; } body { background: url("http://attacker.com/leak"); }'
    app.config.filter_tabs_highlight_color = css_payload

    content = """
Test CSS Injection
==================

.. filter-tabs::

   .. tab:: Test
      Content
"""
    app.srcdir.joinpath("index.rst").write_text(content)
    app.build()

    theme_css_path = app.outdir / "_static" / "filter_tabs_theme.css"
    assert theme_css_path.exists()
    theme_content = theme_css_path.read_text(encoding="utf-8")

    # If it's vulnerable, we'll see the unescaped payload breaking the structure
    # A secure implementation would either validate the color or escape it (though escaping CSS is tricky)
    # Most likely it should be validated as a color string.
    assert "body { background: url" not in theme_content, (
        "CSS injection payload found in generated theme CSS!"
    )
