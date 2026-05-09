"""
Tests for crawler.py

These tests avoid live network calls. They test parsing logic using sample HTML.
"""

from crawler import Crawler


SAMPLE_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">“It is good to have friends.”</span>
      <small class="author">Example Author</small>
      <div class="tags">
        <a class="tag">friendship</a>
        <a class="tag">life</a>
      </div>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
  </body>
</html>
"""


def test_extract_text_collects_quote_author_and_tags():
    crawler = Crawler(delay_seconds=0)
    text = crawler.extract_text(SAMPLE_HTML)

    assert "It is good to have friends" in text
    assert "Example Author" in text
    assert "friendship" in text
    assert "life" in text


def test_find_next_page_returns_absolute_url():
    crawler = Crawler(delay_seconds=0)
    next_url = crawler.find_next_page("https://quotes.toscrape.com/", SAMPLE_HTML)

    assert next_url == "https://quotes.toscrape.com/page/2/"


def test_find_next_page_returns_none_when_missing():
    crawler = Crawler(delay_seconds=0)
    next_url = crawler.find_next_page("https://quotes.toscrape.com/", "<html></html>")

    assert next_url is None
