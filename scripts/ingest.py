"""Run the indexing pipeline: extract → chunk → index.

Usage: python scripts/ingest.py
Writes data/processed/pages.jsonl, data/processed/chunks.jsonl and data/index/.
"""


def main() -> None:
    # TODO: load settings
    # TODO: extract every PDF in data/raw/ → write pages.jsonl
    # TODO: chunk pages → write chunks.jsonl
    # TODO: build the index
    # TODO: print counts per stage (documents, pages, chunks) and timings
    ...


if __name__ == "__main__":
    main()
