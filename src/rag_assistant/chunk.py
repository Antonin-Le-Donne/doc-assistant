"""Stage 2: pages → overlapping chunks that keep their metadata."""

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
    """Split each page into non-empty chunks of at most `size` characters, never across pages."""
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
    # Leaves room for the overlap, so splitting always progresses.
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
    """Split on paragraphs, then lines, sentences, words and characters, as needed."""
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
    """End of `text`, at most `length` characters, starting on a word boundary if possible."""
    if length <= 0:
        return ""
    tail = text[-length:]
    if not text[-length - 1 :][0].isspace():
        boundary = re.search(r"\s", tail)
        if boundary:
            tail = tail[boundary.end() :]
    return tail.strip()
