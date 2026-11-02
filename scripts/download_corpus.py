"""Download the corpus PDFs listed in docs/corpus.md into data/raw/.

Only needed for documents whose licence does not allow committing them.
Usage: python scripts/download_corpus.py
"""

# Direct PDF URLs only (not web pages). Keep in sync with docs/corpus.md.
CORPUS_URLS: dict[str, str] = {
    # "file_name.pdf": "https://...",
}


def main() -> None:
    # TODO: create data/raw if needed
    # TODO: for each entry, skip if the file already exists
    # TODO: download with httpx (follow redirects, timeout), check it really is a PDF
    # TODO: print a summary (downloaded / skipped / failed)
    ...


if __name__ == "__main__":
    main()
