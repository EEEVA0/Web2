"""
Tests for indexer.py
"""

from crawler import CrawledPage
from indexer import Indexer, tokenize


def test_tokenize_is_case_insensitive():
    assert tokenize("Good good GOOD") == ["good", "good", "good"]


def test_tokenize_removes_basic_punctuation():
    assert tokenize("Hello, world!") == ["hello", "world"]


def test_build_index_records_frequency_and_positions():
    pages = [
        CrawledPage(
            url="https://example.com/page1",
            text="Good friends are good.",
        )
    ]

    indexer = Indexer()
    index = indexer.build(pages)

    assert "good" in index
    assert index["good"]["https://example.com/page1"]["frequency"] == 2
    assert index["good"]["https://example.com/page1"]["positions"] == [0, 3]


def test_build_index_records_page_word_count_and_term_density():
    pages = [
        CrawledPage(
            url="https://example.com/page1",
            text="Good friends are good.",
        )
    ]

    indexer = Indexer()
    index = indexer.build(pages)

    posting = index["good"]["https://example.com/page1"]

    assert posting["page_word_count"] == 4
    assert posting["term_density"] == 0.5


def test_build_index_records_document_frequency_and_tfidf():
    pages = [
        CrawledPage(url="page1", text="good friends good"),
        CrawledPage(url="page2", text="good life"),
        CrawledPage(url="page3", text="wisdom life"),
    ]

    indexer = Indexer()
    index = indexer.build(pages)

    assert index["good"]["page1"]["document_frequency"] == 2
    assert index["good"]["page2"]["document_frequency"] == 2
    assert index["good"]["page1"]["tf_idf"] > 0
