"""
crawler.py

Crawler for https://quotes.toscrape.com/

Coursework requirements covered:
- Crawl all pages of the target website.
- Respect a politeness window of at least 6 seconds between successive requests.
- Handle network errors gracefully.
- Extract page text for indexing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_DELAY_SECONDS = 6


@dataclass
class CrawledPage:
    """Represents one crawled page."""

    url: str
    text: str


class Crawler:
    """Crawler for the coursework target website."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        delay_seconds: int = POLITENESS_DELAY_SECONDS,
        timeout: int = 10,
    ) -> None:
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.session = requests.Session()

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML for one URL."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"[ERROR] Failed to fetch {url}: {exc}")
            return None

    def extract_text(self, html: str) -> str:
        """
        Extract searchable text from one HTML page.

        The target website stores each quote in div.quote blocks. We index:
        - quote text
        - author names
        - tags
        """
        soup = BeautifulSoup(html, "html.parser")
        quote_blocks = soup.select("div.quote")

        text_parts: List[str] = []

        for block in quote_blocks:
            quote_text = block.select_one("span.text")
            author = block.select_one("small.author")
            tags = block.select("a.tag")

            if quote_text:
                text_parts.append(quote_text.get_text(" ", strip=True))
            if author:
                text_parts.append(author.get_text(" ", strip=True))
            for tag in tags:
                text_parts.append(tag.get_text(" ", strip=True))

        return " ".join(text_parts)

    def find_next_page(self, current_url: str, html: str) -> Optional[str]:
        """Return the absolute URL of the next page, or None if it does not exist."""
        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.select_one("li.next a")

        if next_link is None:
            return None

        href = next_link.get("href")
        if not href:
            return None

        return urljoin(current_url, href)

    def crawl(self) -> List[CrawledPage]:
        """
        Crawl the full target website.

        The first request starts immediately. Every following request waits
        delay_seconds, satisfying the required 6-second politeness window.
        """
        pages: List[CrawledPage] = []
        current_url: Optional[str] = self.base_url
        is_first_request = True

        while current_url:
            if not is_first_request:
                time.sleep(self.delay_seconds)
            is_first_request = False

            print(f"[CRAWL] Fetching {current_url}")
            html = self.fetch_page(current_url)

            if html is None:
                print("[CRAWL] Stopping because a page could not be fetched.")
                break

            text = self.extract_text(html)
            pages.append(CrawledPage(url=current_url, text=text))

            current_url = self.find_next_page(current_url, html)

        print(f"[CRAWL] Completed. Crawled {len(pages)} page(s).")
        return pages
