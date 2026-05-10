"""
crawler.py

Crawler for https://quotes.toscrape.com/

Coursework requirements covered:
- Crawl pages of the target website.
- Respect a politeness window of at least 6 seconds between successive requests.
- Handle network errors gracefully.
- Extract page text for indexing.

Important improvement:
- The crawler does not only follow pagination links.
- It discovers and follows internal links such as:
  - /page/2/
  - /tag/deep-thoughts/
  - /tag/deep-thoughts/page/1/
  - /author/Albert-Einstein/

Page numbering:
- Each successfully crawled page is assigned a page_id.

Duplicate URL handling:
- /page/1/ is treated as /
- /tag/friends/page/1/ is treated as /tag/friends/

Error handling:
- If a request times out or fails, the crawler retries before skipping the page.
- Request count and saved page_id are separated to avoid confusing output.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Set
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_DELAY_SECONDS = 6
DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_RETRIES = 2


@dataclass
class CrawledPage:
    """Represents one successfully crawled page."""

    page_id: int
    url: str
    text: str


class Crawler:
    """Crawler for the coursework target website."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        delay_seconds: int = POLITENESS_DELAY_SECONDS,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        max_pages: int | None = None,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        self.base_url = self.normalise_url(base_url)
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.max_pages = max_pages
        self.retries = retries
        self.session = requests.Session()

        parsed_base = urlparse(self.base_url)
        self.allowed_domain = parsed_base.netloc

    def normalise_url(self, url: str) -> str:
        """
        Normalise URLs to reduce duplicate crawling.

        Examples:
        - https://quotes.toscrape.com/page/1/
          becomes
          https://quotes.toscrape.com/

        - https://quotes.toscrape.com/tag/friends/page/1/
          becomes
          https://quotes.toscrape.com/tag/friends/
        """
        url, _fragment = urldefrag(url)
        parsed = urlparse(url)

        scheme = parsed.scheme
        netloc = parsed.netloc
        path = parsed.path or "/"

        if path in {"/page/1/", "/page/1"}:
            path = "/"

        if path.endswith("/page/1/"):
            path = path[: -len("page/1/")]

        if path.endswith("/page/1"):
            path = path[: -len("page/1")]

        if not path.endswith("/"):
            path += "/"

        return f"{scheme}://{netloc}{path}"

    def is_allowed_url(self, url: str) -> bool:
        """
        Check whether a URL belongs to the target website and should be crawled.

        This prevents the crawler from leaving quotes.toscrape.com.
        """
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        if parsed.netloc != self.allowed_domain:
            return False

        blocked_paths = {"/login", "/logout"}
        if parsed.path.rstrip("/") in blocked_paths:
            return False

        return True

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML for one URL.

        If the request fails or times out, retry a small number of times.
        This improves robustness while still handling network errors gracefully.
        """
        total_attempts = self.retries + 1

        for attempt in range(1, total_attempts + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text

            except requests.RequestException as exc:
                print(f"[ERROR] Failed to fetch {url} on attempt {attempt}/{total_attempts}: {exc}")

                if attempt < total_attempts:
                    print(
                        f"[CRAWL] Retrying after {self.delay_seconds} seconds..."
                    )
                    time.sleep(self.delay_seconds)
                else:
                    print(f"[CRAWL] Giving up on {url}.")
                    return None

        return None

    def extract_text(self, html: str) -> str:
        """
        Extract searchable text from one HTML page.

        For quote listing and tag pages, this indexes:
        - quote text
        - author names
        - tags

        For author pages, this indexes:
        - author name
        - birth date
        - birth location
        - description
        """
        soup = BeautifulSoup(html, "html.parser")
        text_parts: List[str] = []

        quote_blocks = soup.select("div.quote")
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

        author_title = soup.select_one("h3.author-title")
        author_born_date = soup.select_one("span.author-born-date")
        author_born_location = soup.select_one("span.author-born-location")
        author_description = soup.select_one("div.author-description")

        if author_title:
            text_parts.append(author_title.get_text(" ", strip=True))

        if author_born_date:
            text_parts.append(author_born_date.get_text(" ", strip=True))

        if author_born_location:
            text_parts.append(author_born_location.get_text(" ", strip=True))

        if author_description:
            text_parts.append(author_description.get_text(" ", strip=True))

        if not text_parts:
            for unwanted in soup(["script", "style"]):
                unwanted.extract()

            body = soup.select_one("body")
            if body:
                text_parts.append(body.get_text(" ", strip=True))

        return " ".join(text_parts)

    def extract_internal_links(self, current_url: str, html: str) -> List[str]:
        """
        Extract crawlable internal links from a page.

        This collects all internal links, including:
        - pagination links
        - tag links
        - author links
        """
        soup = BeautifulSoup(html, "html.parser")
        discovered_links: List[str] = []

        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue

            absolute_url = urljoin(current_url, href)
            normalised_url = self.normalise_url(absolute_url)

            if self.is_allowed_url(normalised_url):
                discovered_links.append(normalised_url)

        return discovered_links

    def crawl(self) -> List[CrawledPage]:
        """
        Crawl the target website using a breadth-first crawl frontier.

        The first request starts immediately. Every following request waits
        delay_seconds, satisfying the required 6-second politeness window.

        request_count:
            Counts every attempted request, including failed requests.

        page_id:
            Counts only successfully saved pages.
        """
        pages: List[CrawledPage] = []
        visited: Set[str] = set()
        queued: Set[str] = {self.base_url}
        frontier: Deque[str] = deque([self.base_url])
        is_first_request = True
        request_count = 0

        while frontier:
            if self.max_pages is not None and len(pages) >= self.max_pages:
                print(f"[CRAWL] Reached max_pages={self.max_pages}.")
                break

            current_url = frontier.popleft()
            queued.discard(current_url)

            if current_url in visited:
                continue

            if not is_first_request:
                time.sleep(self.delay_seconds)
            is_first_request = False

            request_count += 1

            html = self.fetch_page(current_url)
            visited.add(current_url)

            if html is None:
                print("[CRAWL] Skipping page because it could not be fetched.")
                continue

            text = self.extract_text(html)

            page_id = len(pages) + 1
            pages.append(
                CrawledPage(
                    page_id=page_id,
                    url=current_url,
                    text=text,
                )
            )

            print(f"[CRAWL] Saved page {page_id}: {current_url}")

            for link in self.extract_internal_links(current_url, html):
                if link not in visited and link not in queued:
                    frontier.append(link)
                    queued.add(link)

        print(f"[CRAWL] Completed. Saved {len(pages)} page(s).")
        print(f"[CRAWL] Total request attempts: {request_count}.")
        return pages