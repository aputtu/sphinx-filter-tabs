import subprocess
import sys
import textwrap

import pytest
from bs4 import BeautifulSoup
from sphinx.testing.util import SphinxTestApp

from tests.helpers import build_index, html_text, read_theme_css


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
    build_index(app, content)

    html_content = html_text(app)

    # Check if the raw payload exists in the HTML
    assert xss_payload not in html_content, "XSS payload found unescaped in HTML!"

    # Check if it's escaped
    soup = BeautifulSoup(html_content, "html.parser")
    label = soup.select_one(".sft-interactive label")
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
    build_index(app, content)

    html_content = html_text(app)

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
    build_index(app, content)

    theme_content = read_theme_css(app)

    # If it's vulnerable, we'll see the unescaped payload breaking the structure
    # A secure implementation would either validate the color or escape it (though escaping CSS is tricky)
    # Most likely it should be validated as a color string.
    assert "body { background: url" not in theme_content, (
        "CSS injection payload found in generated theme CSS!"
    )
    assert "--sft-highlight-color: var(--pst-color-primary" in theme_content
    assert "#007bff" not in theme_content


def test_generated_ids_are_sanitized_for_unusual_docnames(tmp_path, rootdir):
    """Generated tab IDs should not preserve punctuation from source docnames."""
    docname = 'bad" onclick="alert(1)'
    srcdir = tmp_path / "src"
    outdir = tmp_path / "out"
    srcdir.mkdir()
    srcdir.joinpath("conf.py").write_text(
        textwrap.dedent(
            f"""
            import sys

            sys.path.insert(0, {str(rootdir)!r})

            extensions = ["filter_tabs"]
            project = "Security test"
            root_doc = {docname!r}
            html_static_path = []
            """
        ),
        encoding="utf-8",
    )
    srcdir.joinpath(f"{docname}.rst").write_text(
        textwrap.dedent(
            """
            Test
            ====

            .. filter-tabs::

               .. tab:: CLI

                  Content.
            """
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx.cmd.build",
            "-q",
            "-b",
            "html",
            str(srcdir),
            str(outdir),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    html = outdir.joinpath(f"{docname}.html").read_text(encoding="utf-8")
    assert "filter-group-bad&quot;" not in html

    soup = BeautifulSoup(html, "html.parser")
    radio = soup.select_one('.sft-interactive input[type="radio"]')
    assert radio["aria-controls"].startswith("filter-group-bad-onclick-alert-1-")
    label = soup.select_one(".sft-interactive label")
    assert '"' not in label["for"]
