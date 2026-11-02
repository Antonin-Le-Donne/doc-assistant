"""Run the indexing pipeline: extract → chunk → index.

Usage: python scripts/ingest.py
Writes data/processed/pages.jsonl, data/processed/chunks.jsonl and data/index/.
"""

import json
import sys
import time
from pathlib import Path
from typing import Iterable

from rag_assistant.chunk import chunk_pages
from rag_assistant.config import load_settings
from rag_assistant.extract import extract_pages
from rag_assistant.index import build_index, load_embedding_model


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    settings = load_settings()
    pdfs = sorted(settings.raw_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDF in {settings.raw_dir}: run scripts/download_corpus.py first")

    start = time.perf_counter()
    pages = [page for pdf in pdfs for page in extract_pages(pdf)]
    write_jsonl(settings.processed_dir / "pages.jsonl", pages)
    print(f"Extract: {len(pdfs)} documents, {len(pages)} pages ({time.perf_counter() - start:.1f} s)")

    start = time.perf_counter()
    chunks = list(chunk_pages(pages, settings.chunk_size, settings.chunk_overlap))
    write_jsonl(settings.processed_dir / "chunks.jsonl", chunks)
    print(f"Chunk: {len(chunks)} chunks ({time.perf_counter() - start:.1f} s)")

    start = time.perf_counter()
    model = load_embedding_model(settings.embedding_model)
    count = build_index(chunks, model, settings.index_dir, settings.embedding_model)
    print(f"Index: {count} chunks with {settings.embedding_model} ({time.perf_counter() - start:.1f} s)")


if __name__ == "__main__":
    main()
