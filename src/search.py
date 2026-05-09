"""
search.py

Search operations over the inverted index.

Coursework requirements covered:
- print command: print inverted index for a particular word.
- find command: return pages containing single-word or multi-word queries.
- Handle edge cases such as empty queries and non-existent words.

High-score extension:
- Search results are ranked by the sum of TF-IDF scores of query terms.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from indexer import InvertedIndex, tokenize


class SearchEngine:
    """Provides print and find operations over an inverted index."""

    def __init__(self, index: InvertedIndex | None = None) -> None:
        self.index = index or {}

    def set_index(self, index: InvertedIndex) -> None:
        """Replace the current index."""
        self.index = index

    def get_word_index(self, word: str) -> Dict[str, object]:
        """
        Return the inverted index entry for one word.

        Search is case-insensitive.
        """
        tokens = tokenize(word)
        if not tokens:
            return {}

        normalised_word = tokens[0]
        return self.index.get(normalised_word, {})

    def find(self, query: str) -> List[str]:
        """
        Find pages containing all words in the query.

        Multi-word query logic:
        - AND semantics are used.
        - A page is returned only if it contains every query term.

        Ranking logic:
        - Matching pages are sorted by the sum of TF-IDF scores for query terms.
        - Higher scores appear first.
        """
        ranked_results = self.find_ranked(query)
        return [url for url, _score in ranked_results]

    def find_ranked(self, query: str) -> List[Tuple[str, float]]:
        """
        Find matching pages and return ranked results as (url, score).

        The score is the sum of TF-IDF values for the query terms in each
        matching page.
        """
        terms = tokenize(query)

        if not terms:
            return []

        page_sets: List[Set[str]] = []

        for term in terms:
            posting = self.index.get(term)
            if not posting:
                return []
            page_sets.append(set(posting.keys()))

        matching_pages = set.intersection(*page_sets)

        scored_results: List[Tuple[str, float]] = []
        for url in matching_pages:
            score = 0.0
            for term in terms:
                score += float(self.index[term][url].get("tf_idf", 0.0))
            scored_results.append((url, round(score, 6)))

        return sorted(scored_results, key=lambda item: (-item[1], item[0]))

    def format_word_index(self, word: str) -> str:
        """Format one word's inverted index for command-line display."""
        entry = self.get_word_index(word)

        if not entry:
            return f"No index entry found for '{word}'."

        lines = [f"Inverted index for '{word.lower()}':"]

        for url, stats in sorted(entry.items()):
            lines.append(f"- {url}")
            lines.append(f"  frequency: {stats['frequency']}")
            lines.append(f"  positions: {stats['positions']}")
            lines.append(f"  page_word_count: {stats.get('page_word_count', 'N/A')}")
            lines.append(f"  document_frequency: {stats.get('document_frequency', 'N/A')}")
            lines.append(f"  term_density: {stats.get('term_density', 'N/A')}")
            lines.append(f"  tf_idf: {stats.get('tf_idf', 'N/A')}")

        return "\n".join(lines)

    def format_find_results(self, query: str) -> str:
        """Format find results for command-line display."""
        if not tokenize(query):
            return "Empty query. Please enter at least one search term."

        results = self.find_ranked(query)

        if not results:
            return f"No pages found for query: '{query}'."

        lines = [f"Pages containing all query term(s) in '{query}', ranked by TF-IDF:"]
        for url, score in results:
            lines.append(f"- {url}  score={score}")

        return "\n".join(lines)
