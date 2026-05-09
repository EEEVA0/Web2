"""
Tests for search.py
"""

from search import SearchEngine


def sample_index():
    return {
        "good": {
            "page1": {
                "frequency": 2,
                "positions": [0, 3],
                "page_word_count": 4,
                "document_frequency": 2,
                "term_density": 0.5,
                "tf_idf": 0.7,
            },
            "page2": {
                "frequency": 1,
                "positions": [5],
                "page_word_count": 6,
                "document_frequency": 2,
                "term_density": 0.166667,
                "tf_idf": 0.2,
            },
        },
        "friends": {
            "page1": {
                "frequency": 1,
                "positions": [1],
                "page_word_count": 4,
                "document_frequency": 1,
                "term_density": 0.25,
                "tf_idf": 0.5,
            },
        },
        "indifference": {
            "page3": {
                "frequency": 1,
                "positions": [2],
                "page_word_count": 5,
                "document_frequency": 1,
                "term_density": 0.2,
                "tf_idf": 0.6,
            },
        },
    }


def test_get_word_index_is_case_insensitive():
    engine = SearchEngine(sample_index())
    assert engine.get_word_index("GOOD") == sample_index()["good"]


def test_find_single_word_query():
    engine = SearchEngine(sample_index())
    assert engine.find("indifference") == ["page3"]


def test_find_multi_word_query_uses_and_logic():
    engine = SearchEngine(sample_index())
    assert engine.find("good friends") == ["page1"]


def test_find_nonexistent_word_returns_empty_list():
    engine = SearchEngine(sample_index())
    assert engine.find("missingword") == []


def test_find_empty_query_returns_empty_list():
    engine = SearchEngine(sample_index())
    assert engine.find("") == []


def test_find_results_are_ranked_by_tfidf():
    engine = SearchEngine(sample_index())
    assert engine.find("good") == ["page1", "page2"]


def test_format_word_index_includes_new_statistics():
    engine = SearchEngine(sample_index())
    output = engine.format_word_index("good")

    assert "term_density" in output
    assert "tf_idf" in output
    assert "page_word_count" in output
    assert "document_frequency" in output
