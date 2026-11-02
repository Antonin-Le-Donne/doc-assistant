"""Stage 2: pages → overlapping chunks that keep their metadata. See SPEC.md §5 (Chunk)."""

from typing import Iterable, Iterator, TypedDict

from rag_assistant.extract import Page


class Chunk(TypedDict):
    chunk_id: str  # "{doc_id}:{page}:{n}"
    doc_id: str
    doc_title: str
    section: str | None
    page: int
    text: str
    char_count: int


def chunk_pages(pages: Iterable[Page], size: int, overlap: int) -> Iterator[Chunk]:
    """Split each page's text into chunks of ~`size` characters with `overlap`.

    Rules:
    - a chunk never mixes two documents;
    - prefer cutting at a paragraph or sentence boundary rather than mid-word;
    - whether a chunk may span two pages is a decision to log (docs/decisions.md).
    """
    # TODO: iterate pages, split text into candidate units (paragraphs, sentences)
    # TODO: accumulate units until size is reached, then emit a Chunk
    # TODO: start the next chunk with the last `overlap` characters
    # TODO: build chunk_id and char_count
    ...
