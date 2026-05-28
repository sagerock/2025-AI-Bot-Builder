"""Tests for cairn/seed_qdrant.py chunk_text helper."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cairn.seed_qdrant import chunk_text, extract_text_from_html


def test_chunk_text_splits_long_input():
    """chunk_text splits text into overlapping pieces of ~size chars."""
    text = "A" * 2500
    chunks = chunk_text(text, size=800, overlap=100)
    assert len(chunks) >= 3
    # Each chunk no bigger than size
    for c in chunks:
        assert len(c) <= 800
    # Consecutive chunks overlap by ~100 chars
    assert chunks[0][-50:] == chunks[1][:50] or chunks[0][-100:] == chunks[1][:100]


def test_chunk_text_returns_single_chunk_for_short_input():
    text = "short text"
    chunks = chunk_text(text, size=800, overlap=100)
    assert chunks == ["short text"]


def test_extract_text_from_html_strips_tags_and_scripts():
    html = """
    <html>
      <head><script>alert('hi')</script><style>body{}</style></head>
      <body>
        <h1>Title</h1>
        <p>First paragraph.</p>
        <script>more = 'evil';</script>
        <p>Second paragraph.</p>
      </body>
    </html>
    """
    text = extract_text_from_html(html)
    assert "Title" in text
    assert "First paragraph" in text
    assert "Second paragraph" in text
    assert "alert" not in text
    assert "evil" not in text
    assert "<script>" not in text
