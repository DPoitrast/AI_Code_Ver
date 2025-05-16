from bs4 import BeautifulSoup
import ai_readiness_checker as arc


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def test_check_semantic_html():
    good = make_soup('<header></header><main></main>')
    bad = make_soup('<div></div>')
    assert arc.check_semantic_html(good)[0] is True
    assert arc.check_semantic_html(bad)[0] is False


def test_check_schema_markup():
    html = '<script type="application/ld+json">{"@context":"schema.org"}</script>'
    soup = make_soup(html)
    missing = make_soup('<script></script>')
    assert arc.check_schema_markup(soup)[0] is True
    assert arc.check_schema_markup(missing)[0] is False


def test_check_headings_structure():
    soup = make_soup('<h1>Title</h1>')
    empty = make_soup('<div></div>')
    assert arc.check_headings_structure(soup)[0] is True
    assert arc.check_headings_structure(empty)[0] is False


def test_check_alt_text():
    soup = make_soup('<img alt="test"/>')
    bad = make_soup('<img/>')
    assert arc.check_alt_text(soup)[0] is True
    assert arc.check_alt_text(bad)[0] is False


def test_check_lists_and_tables():
    soup = make_soup('<ul><li>A</li></ul>')
    bad = make_soup('<div></div>')
    assert arc.check_lists_and_tables(soup)[0] is True
    assert arc.check_lists_and_tables(bad)[0] is False


def test_check_language_attribute():
    soup = make_soup('<html lang="en"></html>')
    bad = make_soup('<html></html>')
    assert arc.check_language_attribute(soup)[0] is True
    assert arc.check_language_attribute(bad)[0] is False


def test_check_transcripts_captions():
    html = '<video aria-label="v"></video><audio aria-label="a"></audio>'
    soup = make_soup(html)
    bad = make_soup('<video></video>')
    assert arc.check_transcripts_captions(soup)[0] is True
    assert arc.check_transcripts_captions(bad)[0] is False
