# Search Engine Tool

This repository implements a Python command-line search engine tool for the COMP/XJCO3011 Coursework 2 assignment.

The tool crawls the required target website, builds an inverted index, saves the index to the file system, loads the saved index, and allows users to search for pages containing specific search terms.

Target website: <https://quotes.toscrape.com/>

This project is designed as an individual practical implementation of a small search engine pipeline, including crawling, indexing, storage, retrieval, testing, and command-line interaction.

---

## 1. Project Overview

The search tool performs four main tasks:

- Crawls pages from the target website.
- Extracts searchable text from quote pages, tag pages, and author pages.
- Builds an inverted index containing word-level statistics for each page.
- Provides a command-line interface with the required commands:

```
build
load
print <word>
find <query terms>
```

The implementation focuses on correctness, modularity, testability, and clear explanation of design decisions. The code is organised into separate crawler, indexer, search, and command-line interface modules.

---

## 2. Key Features

### 2.1 Crawling

- Crawls pages from <https://quotes.toscrape.com/>.
- Uses a breadth-first crawl frontier to discover internal links.
- Follows internal links including:
  - homepage pagination links
  - tag pages
  - tag pagination pages
  - author detail pages
- Ignores external websites.
- Ignores login/logout pages because they are not useful for search indexing.
- Applies URL normalisation to avoid duplicate crawling.

Examples of duplicate URL handling:

`https://quotes.toscrape.com/page/1/` is treated as `https://quotes.toscrape.com/`

`https://quotes.toscrape.com/tag/friends/page/1/` is treated as `https://quotes.toscrape.com/tag/friends/`

### 2.2 Politeness Window

The crawler respects a politeness window of at least 6 seconds between successive requests to the website.

This is implemented using:

```python
import time
time.sleep(6)
```

between requests.

### 2.3 Error Handling

The crawler handles network errors gracefully. If a request fails or times out:

- the crawler retries the request a limited number of times;
- if all attempts fail, the page is skipped;
- the program continues crawling other pages instead of crashing.

This is important because network requests may fail unpredictably.

### 2.4 Inverted Index

The tool builds a case-insensitive inverted index. For example, `Good`, `GOOD`, and `good` are treated as the same word.

The index stores the following statistics for each word in each page:

- `page_id`
- `frequency`
- `positions`
- `page_word_count`
- `document_frequency`
- `term_density`
- `tf_idf`

### 2.5 Search

The tool supports:

- single-word queries;
- multi-word queries;
- empty query handling;
- non-existent word handling;
- TF-IDF-based result ranking.

For multi-word queries, the tool uses AND logic. This means a page is returned only if it contains all query terms. For example:

```
find good friends
```

returns pages that contain both `good` and `friends`.

---

## 3. Repository Structure

```
repository-name/
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── index.json
├── requirements.txt
└── README.md
```

### Module Responsibilities

| File | Responsibility |
|------|---------------|
| `src/crawler.py` | Crawls the target website, extracts page text, follows internal links, handles URL normalisation and network errors |
| `src/indexer.py` | Tokenises text, builds the inverted index, calculates word statistics, saves and loads the index |
| `src/search.py` | Implements `print` and `find` search logic, including TF-IDF ranking |
| `src/main.py` | Provides the interactive command-line interface |
| `tests/test_crawler.py` | Tests HTML parsing, link extraction, URL filtering, and URL normalisation |
| `tests/test_indexer.py` | Tests tokenisation, index construction, word statistics, and TF-IDF calculation |
| `tests/test_search.py` | Tests single-word search, multi-word search, ranking, and edge cases |
| `tests/conftest.py` | Configures pytest import paths |
| `data/index.json` | Stores the compiled inverted index after running `build` |

---

## 4. Installation and Setup

### 4.1 Clone or Download the Repository

If using Git:

```bash
git clone <your-repository-url>
cd <repository-name>
```

If using a downloaded folder, open a terminal in the project root directory.

The project root should contain:

```
src/
tests/
data/
requirements.txt
README.md
```

### 4.2 Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

### 4.3 Install Dependencies

```bash
pip install -r requirements.txt
```

Required dependencies:

```
requests
beautifulsoup4
pytest
pytest-cov
```

---

## 5. Usage

Run the command-line interface from the project root:

```bash
python src/main.py
```

You should then see an interactive prompt:

```
>
```

The available commands are:

```
build
load
print <word>
find <query terms>
help
exit
```

---

## 6. Command Examples

### 6.1 `build`

The `build` command crawls the website, builds the inverted index, and saves it to `data/index.json`.

```
> build
```

Expected behaviour:

```
[CRAWL] Saved page 1: https://quotes.toscrape.com/
[CRAWL] Saved page 2: https://quotes.toscrape.com/author/Albert-Einstein/
...
[CRAWL] Completed. Saved X page(s).
[BUILD] Index built successfully.
[BUILD] Indexed X unique word(s).
[BUILD] Saved index to data/index.json
```

The exact number of pages and words may vary depending on the crawl scope and network availability.

### 6.2 `load`

The `load` command loads the previously saved index from `data/index.json`.

```
> load
```

Expected behaviour:

```
[LOAD] Index loaded successfully from data/index.json
[LOAD] Loaded X unique word(s).
```

If the index file does not exist, the tool displays:

```
[LOAD] Index file not found. Please run 'build' first.
```

### 6.3 `print`

The `print` command prints the inverted index entry for one word.

```
> print good
```

Example output:

```
Inverted index for 'good':
- https://quotes.toscrape.com/
  page_id: 1
  frequency: 2
  positions: [15, 88]
  page_word_count: 228
  document_frequency: 8
  term_density: 0.008772
  tf_idf: 0.010527
```

If the word is not found:

```
No index entry found for 'missingword'.
```

### 6.4 `find`

The `find` command returns pages containing all query terms.

Single-word query:

```
> find indifference
```

Multi-word query:

```
> find good friends
```

Example output:

```
Pages containing all query term(s) in 'good friends', ranked by TF-IDF:
- https://quotes.toscrape.com/page/7/  score=0.032184
- https://quotes.toscrape.com/tag/friends/  score=0.018392
```

Empty query example:

```
> find
```

Expected output:

```
Empty query. Please enter at least one search term.
```

---

## 7. Inverted Index Design

The inverted index uses a nested dictionary structure:

```json
{
    "word": {
        "url": {
            "page_id": 1,
            "frequency": 2,
            "positions": [3, 17],
            "page_word_count": 120,
            "document_frequency": 5,
            "term_density": 0.0167,
            "tf_idf": 0.42
        }
    }
}
```

### 7.1 Field Explanation

| Field | Meaning |
|-------|---------|
| `page_id` | Sequential ID assigned to each successfully crawled page |
| `frequency` | Number of times the word appears in the page |
| `positions` | Zero-based token positions of the word in the page |
| `page_word_count` | Total number of tokens in the page |
| `document_frequency` | Number of pages containing the word |
| `term_density` | Word frequency divided by page word count |
| `tf_idf` | Ranking-related score based on term frequency and inverse document frequency |

### 7.2 Why This Structure Was Chosen

The nested dictionary allows direct lookup by word:

```python
index[word]
```

This makes the `print <word>` command efficient because the tool can immediately retrieve all pages containing that word.

For each word, the index stores page-level postings. This allows the tool to support both:

- exact inverted index inspection through `print`;
- page retrieval and ranking through `find`.

This design also makes it easy to extend the search tool with more advanced ranking or query processing features.

---

## 8. TF-IDF Ranking

The tool includes TF-IDF ranking as an advanced feature.

The formula used is:

```
TF  = frequency / page_word_count
IDF = log((1 + total_pages) / (1 + document_frequency)) + 1
TF-IDF = TF × IDF
```

Smoothing is used in the IDF formula to avoid division-by-zero issues and keep the score stable.

### Why TF-IDF Is Useful

A word may appear many times in one page, but if it also appears in almost every page, it is not very distinctive. For example, common words such as `it`, `the`, and `and` may have relatively high frequency but low distinctiveness. By contrast, rarer terms are often more useful for identifying relevant pages.

The `find` command ranks matching pages by summing the TF-IDF scores of all query terms in each matching page.

---

## 9. Crawler Design

The crawler uses a breadth-first crawl frontier. It starts from <https://quotes.toscrape.com/> and then discovers and follows internal links.

### 9.1 Crawl Frontier

The crawler maintains:

| Variable | Purpose |
|----------|---------|
| `frontier` | Queue of URLs waiting to be crawled |
| `visited` | URLs that have already been requested |
| `queued` | URLs already added to the frontier |

This prevents repeated crawling of the same URL.

### 9.2 URL Normalisation

Before a URL is added to the frontier, it is normalised.

Examples:

- `https://quotes.toscrape.com/page/1/` → `https://quotes.toscrape.com/`
- `https://quotes.toscrape.com/tag/friends/page/1/` → `https://quotes.toscrape.com/tag/friends/`

This prevents duplicate crawling and duplicate index entries.

### 9.3 Text Extraction

The crawler extracts text from:

- quote text;
- author names;
- quote tags;
- author title;
- author birth date;
- author birth location;
- author description.

This allows both quote listing pages and author detail pages to be indexed.

### 9.4 Network Error Handling

If a request fails or times out, the crawler retries before skipping the page. Skipped pages are not added to the inverted index. This keeps the program robust even when the network is unstable.

---

## 10. Testing

The project uses pytest.

Run all tests:

```bash
pytest
```

Run only crawler tests:

```bash
pytest tests/test_crawler.py
```

Run only indexer tests:

```bash
pytest tests/test_indexer.py
```

Run only search tests:

```bash
pytest tests/test_search.py
```

Run tests with coverage:

```bash
pytest --cov=src
```

Run tests with a detailed coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

### 10.1 Test Coverage

The test suite covers:

- quote page text extraction;
- author page text extraction;
- internal link discovery;
- pagination link discovery;
- tag link discovery;
- author link discovery;
- external link filtering;
- login/logout link filtering;
- URL normalisation;
- duplicate URL prevention;
- tokenisation;
- case-insensitive indexing;
- frequency recording;
- position recording;
- page ID recording;
- page word count calculation;
- document frequency calculation;
- term density calculation;
- TF-IDF calculation;
- single-word search;
- multi-word search;
- AND query logic;
- TF-IDF ranking;
- empty query handling;
- non-existent word handling.

The crawler tests use sample HTML rather than live network requests. This makes the tests faster, more stable, and independent of temporary website or network issues.
