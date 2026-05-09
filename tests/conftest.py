"""
pytest configuration.

Adds src/ to sys.path so tests can import crawler.py, indexer.py, and search.py
when pytest is run from the repository root.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
