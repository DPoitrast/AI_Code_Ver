import pytest
from bs4 import BeautifulSoup

from analyze_website import check_schema_markup, check_alt_text


def test_schema_markup_case_insensitivity():
    html_variants = [
        '<script type="application/ld+json">{"@context": "https://schema.org"}</script>',
        '<script type="application/ld+json">{"@context": "https://Schema.org"}</script>',
        '<script type="application/ld+json">{"@context": "HTTPS://SCHEMA.ORG"}</script>',
    ]
    for html in html_variants:
        soup = BeautifulSoup(html, "html.parser")
        passed, _ = check_schema_markup(soup)
        assert passed


def test_alt_text_no_images():
    html = "<html><head></head><body><p>No images here</p></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    passed, message = check_alt_text(soup)
    assert passed
    assert message == "No images found."

