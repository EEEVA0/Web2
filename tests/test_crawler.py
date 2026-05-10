"""
Tests for crawler.py.

These tests avoid live network calls. They test parsing and link discovery logic
using sample HTML.
"""

from crawler import Crawler


QUOTE_PAGE_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">“It is good to have friends.”</span>
      <small class="author">Example Author</small>
      <a href="/author/Example-Author/">(about)</a>
      <div class="tags">
        <a class="tag" href="/tag/friendship/">friendship</a>
        <a class="tag" href="/tag/life/">life</a>
      </div>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
    <a href="https://external.example.com/">External</a>
    <a href="/login">Login</a>
  </body>
</html>
"""


AUTHOR_PAGE_HTML = """
<html>
  <body>
    <h3 class="author-title">Albert Einstein</h3>
    <span class="author-born-date">March 14, 1879</span>
    <span class="author-born-location">in Ulm, Germany</span>
    <div class="author-description">
      Albert Einstein was a German-born theoretical physicist.
    </div>
  </body>
</html>
"""


def test_extract_text_collects_quote_author_and_tags():
    crawler = Crawler(delay_seconds=0)
    text = crawler.extract_text(QUOTE_PAGE_HTML)

    assert "It is good to have friends" in text
    assert "Example Author" in text
    assert "friendship" in text
    assert "life" in text


def test_extract_text_collects_author_page_details():
    crawler = Crawler(delay_seconds=0)
    text = crawler.extract_text(AUTHOR_PAGE_HTML)

    assert "Albert Einstein" in text
    assert "March 14, 1879" in text
    assert "Ulm, Germany" in text
    assert "theoretical physicist" in text


def test_extract_internal_links_includes_pagination_author_and_tag_links():
    crawler = Crawler(delay_seconds=0)
    links = crawler.extract_internal_links("https://quotes.toscrape.com/", QUOTE_PAGE_HTML)

    assert "https://quotes.toscrape.com/page/2/" in links
    assert "https://quotes.toscrape.com/author/Example-Author/" in links
    assert "https://quotes.toscrape.com/tag/friendship/" in links
    assert "https://quotes.toscrape.com/tag/life/" in links


def test_extract_internal_links_excludes_external_and_login_links():
    crawler = Crawler(delay_seconds=0)
    links = crawler.extract_internal_links("https://quotes.toscrape.com/", QUOTE_PAGE_HTML)

    assert "https://external.example.com/" not in links
    assert "https://quotes.toscrape.com/login" not in links


def test_is_allowed_url_accepts_target_site_only():
    crawler = Crawler(delay_seconds=0)

    assert crawler.is_allowed_url("https://quotes.toscrape.com/tag/life/")
    assert not crawler.is_allowed_url("https://external.example.com/")
