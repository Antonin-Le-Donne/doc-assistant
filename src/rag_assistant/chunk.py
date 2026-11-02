"""Stage 2: pages → overlapping chunks that keep their metadata. See SPEC.md §5 (Chunk)."""

import re
from typing import Iterable, Iterator, TypedDict

from rag_assistant.extract import Page

SEPARATOR = "\n"


class Chunk(TypedDict):
    chunk_id: str  # "{doc_id}:{page}:{n}"
    doc_id: str
    doc_title: str
    section: str | None
    page: int
    text: str
    char_count: int


def chunk_pages(pages: Iterable[Page], size: int, overlap: int) -> Iterator[Chunk]:
    """Split each page's text into chunks of at most `size` characters with `overlap`.

    Rules (docs/decisions.md):
    - a chunk never mixes two documents or two pages;
    - prefer cutting at a paragraph or sentence boundary rather than mid-word;
    - len(text) <= size always holds, and no chunk is empty.
    """
    if size <= 0 or not 0 < overlap < size:
        raise ValueError(f"need 0 < overlap < size, got overlap={overlap} and size={size}")
    for page in pages:
        for n, text in enumerate(_split_text(page["text"], size, overlap)):
            yield Chunk(
                chunk_id=f"{page['doc_id']}:{page['page']}:{n}",
                doc_id=page["doc_id"],
                doc_title=page["doc_title"],
                section=page["section"],
                page=page["page"],
                text=text,
                char_count=len(text),
            )


def _split_text(text: str, size: int, overlap: int) -> Iterator[str]:
    # A unit must still fit after the overlap and separator, or splitting cannot progress.
    max_unit = max(1, size - overlap - len(SEPARATOR))
    current = ""
    for unit in _units(text, max_unit):
        if not current:
            current = unit
        elif len(current) + len(SEPARATOR) + len(unit) <= size:
            current += SEPARATOR + unit
        else:
            yield current
            room = size - len(unit) - len(SEPARATOR)
            tail = _tail(current, min(overlap, room))
            current = tail + SEPARATOR + unit if tail else unit
    if current:
        yield current


def _units(text: str, max_length: int) -> Iterator[str]:
    """Paragraphs, then lines, sentences, words and finally characters, as far as needed."""
    for pattern in (r"\n\s*\n", r"\n", r"(?<=[.!?;:])\s+", r"\s+"):
        if len(text.strip()) <= max_length:
            break
        parts = [part.strip() for part in re.split(pattern, text) if part.strip()]
        if len(parts) > 1:
            for part in parts:
                yield from _units(part, max_length)
            return
    text = text.strip()
    for start in range(0, len(text), max_length):
        yield text[start : start + max_length]


def _tail(text: str, length: int) -> str:
    """The last `length` characters at most, starting on a word boundary when one exists."""
    if length <= 0:
        return ""
    tail = text[-length:]
    if not text[-length - 1 :][0].isspace():
        boundary = re.search(r"\s", tail)
        if boundary:
            tail = tail[boundary.end() :]
    return tail.strip()
