"""
main.py

Command-line interface for the search engine tool.

Required commands:
- build
- load
- print <word>
- find <query terms>
"""

from __future__ import annotations

from pathlib import Path

from crawler import Crawler
from indexer import Indexer
from search import SearchEngine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = PROJECT_ROOT / "data" / "index.json"


class SearchToolCLI:
    """Interactive command-line interface."""

    def __init__(self) -> None:
        self.indexer = Indexer()
        self.search_engine = SearchEngine()

    def build(self) -> None:
        """Crawl the website, build the index, and save it."""
        crawler = Crawler()
        pages = crawler.crawl()

        if not pages:
            print("[BUILD] No pages were crawled. Index was not created.")
            return

        index = self.indexer.build(pages)
        self.indexer.save(INDEX_FILE)
        self.search_engine.set_index(index)

        print("[BUILD] Index built successfully.")
        print(f"[BUILD] Indexed {len(index)} unique word(s).")
        print(f"[BUILD] Saved index to {INDEX_FILE}")

    def load(self) -> None:
        """Load an existing index from the file system."""
        try:
            index = self.indexer.load(INDEX_FILE)
        except FileNotFoundError:
            print("[LOAD] Index file not found. Please run 'build' first.")
            return

        self.search_engine.set_index(index)
        print(f"[LOAD] Index loaded successfully from {INDEX_FILE}")
        print(f"[LOAD] Loaded {len(index)} unique word(s).")

    def print_word(self, word: str) -> None:
        """Print the inverted index for one word."""
        if not word.strip():
            print("Usage: print <word>")
            return

        print(self.search_engine.format_word_index(word))

    def find(self, query: str) -> None:
        """Find pages containing the query term(s)."""
        print(self.search_engine.format_find_results(query))

    def handle_command(self, command: str) -> bool:
        """Handle one user command."""
        command = command.strip()

        if not command:
            print("Please enter a command. Available commands: build, load, print, find, exit")
            return True

        parts = command.split(maxsplit=1)
        action = parts[0].lower()
        argument = parts[1] if len(parts) > 1 else ""

        if action == "build":
            self.build()
        elif action == "load":
            self.load()
        elif action == "print":
            self.print_word(argument)
        elif action == "find":
            self.find(argument)
        elif action in {"exit", "quit"}:
            print("Goodbye.")
            return False
        elif action == "help":
            self.show_help()
        else:
            print(f"Unknown command: {action}")
            self.show_help()

        return True

    def show_help(self) -> None:
        """Print command usage information."""
        print(
            "\nAvailable commands:\n"
            "  build                 Crawl the website, build the index, and save it\n"
            "  load                  Load the saved index from the file system\n"
            "  print <word>          Print the inverted index for one word\n"
            "  find <query terms>    Find pages containing all query terms, ranked by TF-IDF\n"
            "  help                  Show this help message\n"
            "  exit                  Exit the program\n"
        )

    def run(self) -> None:
        """Run the interactive command-line shell."""
        print("Search Engine Tool for https://quotes.toscrape.com/")
        self.show_help()

        while True:
            command = input("> ")
            should_continue = self.handle_command(command)

            if not should_continue:
                break


def main() -> None:
    """Program entry point."""
    cli = SearchToolCLI()
    cli.run()


if __name__ == "__main__":
    main()
