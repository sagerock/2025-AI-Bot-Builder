"""Seed the Cairn Qdrant collection from a YAML page list.

Usage:
    python cairn/seed_qdrant.py [--dry-run]

Reads cairn/knowledge_pages.yaml, fetches each URL, extracts main text,
chunks it, embeds each chunk via the existing embedding_service, and uploads
to the configured Qdrant collection. Clears the collection before re-seeding
so the script is idempotent.

Requires QDRANT_URL, QDRANT_API_KEY, DEFAULT_OPENAI_API_KEY (for embeddings)
in the environment.
"""
import argparse
import sys
import time
from pathlib import Path

import httpx
import yaml
from bs4 import BeautifulSoup

# Make app importable when run as a script
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.qdrant_service import qdrant_service  # noqa: E402
from app.services.embedding_service import embedding_service  # noqa: E402


def extract_text_from_html(html: str) -> str:
    """Pull readable text out of an HTML page. Drops scripts, styles, nav, footer."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Collapse whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping windows of `size` chars."""
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def fetch_page(url: str, timeout: float = 20.0) -> str:
    response = httpx.get(url, timeout=timeout, follow_redirects=True,
                         headers={"User-Agent": "Cairn-Seed-Bot/1.0"})
    response.raise_for_status()
    return response.text


def seed(config_path: Path, dry_run: bool = False) -> None:
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    collection = cfg["collection"]
    chunk_size = cfg.get("chunk_size", 800)
    overlap = cfg.get("chunk_overlap", 100)
    pages = cfg.get("pages", [])

    print(f"Seeding {len(pages)} pages into Qdrant collection '{collection}' "
          f"(chunk_size={chunk_size}, overlap={overlap})")

    all_texts = []
    all_metadatas = []

    for page in pages:
        url = page["url"]
        label = page.get("label", url)
        print(f"  Fetching {label} ({url})")
        try:
            html = fetch_page(url)
        except Exception as e:
            print(f"    SKIP -- fetch failed: {e}")
            continue
        text = extract_text_from_html(html)
        chunks = chunk_text(text, size=chunk_size, overlap=overlap)
        print(f"    {len(text)} chars -> {len(chunks)} chunks")
        for chunk in chunks:
            all_texts.append(chunk)
            all_metadatas.append({"source": url, "label": label})

    if dry_run:
        print(f"\nDRY RUN -- would upload {len(all_texts)} chunks. Exiting.")
        return

    # Generate all embeddings up front
    print(f"\nGenerating embeddings for {len(all_texts)} chunks...")
    all_embeddings = []
    for i, text in enumerate(all_texts):
        embedding = embedding_service.generate_embedding(text)
        all_embeddings.append(embedding)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(all_texts)} embedded")

    # Reset the collection then bulk upload via upload_points
    print(f"\nResetting collection '{collection}'...")
    if qdrant_service.collection_exists(collection):
        qdrant_service.delete_collection(collection)
    qdrant_service.create_collection(collection)

    print(f"Uploading {len(all_texts)} points...")
    # upload_points handles batching internally; call in slices to report progress
    batch_size = 100
    for i in range(0, len(all_texts), batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_embeddings = all_embeddings[i:i + batch_size]
        batch_metadatas = all_metadatas[i:i + batch_size]
        qdrant_service.upload_points(collection, batch_texts, batch_embeddings, batch_metadatas)
        print(f"  batch {i // batch_size + 1}: {len(batch_texts)} points uploaded")
        time.sleep(0.2)
    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Seed Cairn's Qdrant collection")
    parser.add_argument("--config", type=Path,
                        default=Path(__file__).parent / "knowledge_pages.yaml",
                        help="Path to knowledge_pages.yaml")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and chunk but don't upload to Qdrant")
    args = parser.parse_args()
    seed(args.config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
