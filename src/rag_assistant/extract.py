"""Stage 1: PDF → pages with metadata. See SPEC.md §5 (Page)."""

from pathlib import Path
from typing import Iterator, TypedDict


class Page(TypedDict):
    doc_id: str
    doc_title: str
    page: int
    section: str | None
    text: str


def make_doc_id(pdf_path: Path) -> str:
    """Stable slug from the file name (lowercase, no spaces or accents)."""
    # TODO
    ...


def extract_pages(pdf_path: Path) -> Iterator[Page]:
    """Yield one Page per PDF page, 1-based page numbers.

    Section detection: track the most recent heading seen so far
    (headings are usually lines in a larger or bold font).
    """
    # TODO: open the PDF, read the document title from its metadata (fallbacks in SPEC)
    # TODO: for each page, get text blocks/spans WITH their font size
    # TODO: decide what counts as a heading, update the current section
    # TODO: clean the text (see clean_text) and yield a Page
    ...


def clean_text(text: str, repeated_lines: set[str]) -> str:
    """Remove repeated headers/footers and fix broken hyphenation."""
    # TODO: drop lines present in repeated_lines
    # TODO: join words split by a hyphen at the end of a line
    # TODO: normalise whitespace
    ...


def find_repeated_lines(pdf_path: Path, min_share: float = 0.5) -> set[str]:
    """Lines that appear on at least `min_share` of the pages (headers, footers)."""
    # TODO
    ...
