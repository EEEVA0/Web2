"""
indexer.py

Builds, saves, and loads an inverted index.

Enhanced index structure:
{
    "word": {
        "url": {
            "frequency": 2,
            "positions": [4, 18],
            "page_word_count": 120,
            "document_frequency": 5,
            "term_density": 0.0167,
            "tf_idf": 0.42
        }
    }
}

Coursework requirements covered:
- Store word statistics, including frequency and positions.
- Treat words case-insensitively.
- Save/load index from the file system.

High-score extension:
- Store ranking-related statistics:
  - page_word_count
  - document_frequency
  - term_density
  - tf_idf
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, List, TypedDict

from crawler import CrawledPage


class PagePosting(TypedDict):
    """Statistics for one word in one page."""

    page_id: int
    frequency: int
    positions: List[int]
    page_word_count: int
    document_frequency: int
    term_density: float
    tf_idf: float


InvertedIndex = Dict[str, Dict[str, PagePosting]]

WORD_PATTERN = re.compile(r"[A-Za-z0-9']+")


def tokenize(text: str) -> List[str]:
    """Tokenise text into lowercase words."""
    return [match.group(0).lower() for match in WORD_PATTERN.finditer(text)]


class Indexer:
    """Builds and persists an inverted index."""

    def __init__(self) -> None:
        self.index: InvertedIndex = {}

    def build(self, pages: List[CrawledPage]) -> InvertedIndex:
        """
        Build the inverted index from crawled pages.

        Statistics recorded for each word-page pair:
        - frequency: how many times the word appears in the page
        - positions: zero-based token positions of the word in the page
        - page_word_count: total number of tokens in the page
        - document_frequency: number of pages containing this word
        - term_density: frequency / page_word_count
        - tf_idf: TF-IDF score for this word in this page

        TF-IDF design:
        - TF = frequency / page_word_count
        - IDF = log((1 + total_pages) / (1 + document_frequency)) + 1

        Smoothing is used in IDF to avoid division by zero and to keep the
        score stable even when a word appears in all pages.
        """
        self.index = {}
        page_token_counts: Dict[str, int] = {}

        # First pass: collect frequency and positions.
        for page in pages:
            tokens = tokenize(page.text)
            page_word_count = len(tokens)
            page_token_counts[page.url] = page_word_count

            for position, word in enumerate(tokens):
                if word not in self.index:
                    self.index[word] = {}

                if page.url not in self.index[word]:
                    self.index[word][page.url] = {
                        "page_id": page.page_id,
                        "frequency": 0,
                        "positions": [],
                        "page_word_count": page_word_count,
                        "document_frequency": 0,
                        "term_density": 0.0,
                        "tf_idf": 0.0,
                    }

                posting = self.index[word][page.url]
                posting["frequency"] += 1
                posting["positions"].append(position)

        # Second pass: calculate document_frequency, term_density, and tf_idf.
        total_pages = len(pages)

        for word, page_postings in self.index.items():
            document_frequency = len(page_postings)
            idf = math.log((1 + total_pages) / (1 + document_frequency)) + 1

            for url, posting in page_postings.items():
                page_word_count = page_token_counts[url]
                frequency = posting["frequency"]

                if page_word_count == 0:
                    term_density = 0.0
                else:
                    term_density = frequency / page_word_count

                posting["page_word_count"] = page_word_count
                posting["document_frequency"] = document_frequency
                posting["term_density"] = round(term_density, 6)
                posting["tf_idf"] = round(term_density * idf, 6)

        return self.index

    def save(self, file_path: str | Path) -> None:
        """Save the current index as JSON."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(self.index, file, indent=2, ensure_ascii=False)

    def load(self, file_path: str | Path) -> InvertedIndex:
        """Load an index from JSON."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Index file not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            loaded_index = json.load(file)

        self.index = loaded_index
        return self.index
