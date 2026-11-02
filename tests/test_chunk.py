"""Chunking rules from docs/decisions.md: hard size limit, progress, one page per chunk."""

import pytest

from rag_assistant.chunk import chunk_pages


def page(text: str, number: int = 1) -> dict:
    return {"doc_id": "doc", "doc_title": "Doc", "page": number, "section": "1 Intro", "text": text}


@pytest.mark.parametrize(
    "text",
    [
        "Une phrase courte. " * 200,
        "premier paragraphe\n\n" * 100,
        "x" * 5000,
        "mot " * 1000,
    ],
)
@pytest.mark.parametrize("size, overlap", [(1000, 150), (500, 150), (50, 49), (2, 1)])
def test_chunks_respect_the_hard_limit_and_are_never_empty(text, size, overlap):
    chunks = list(chunk_pages([page(text)], size, overlap))
    assert chunks
    for chunk in chunks:
        assert 0 < len(chunk["text"]) <= size
        assert chunk["char_count"] == len(chunk["text"])


def test_next_chunk_starts_with_the_end_of_the_previous_one():
    words = " ".join(f"mot{i}" for i in range(300))
    first, second, *_ = chunk_pages([page(words)], size=200, overlap=40)
    start = second["text"].split()[0]
    assert start in first["text"][-40:]


def test_chunks_never_span_two_pages_and_keep_metadata():
    chunks = list(chunk_pages([page("texte de la page un", 1), page("texte de la page deux", 2)], 1000, 150))
    assert [(chunk["chunk_id"], chunk["page"]) for chunk in chunks] == [("doc:1:0", 1), ("doc:2:0", 2)]
    assert chunks[1]["text"] == "texte de la page deux"
    assert chunks[1]["section"] == "1 Intro"


def test_empty_page_gives_no_chunk():
    assert list(chunk_pages([page("")], 1000, 150)) == []


@pytest.mark.parametrize("size, overlap", [(0, 0), (100, 100), (100, 150), (100, 0)])
def test_invalid_settings_are_rejected(size, overlap):
    with pytest.raises(ValueError):
        list(chunk_pages([page("texte")], size, overlap))
