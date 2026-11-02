"""Stage 4: question → top-k chunks with scores."""

from typing import TypedDict


class RetrievedChunk(TypedDict):
    chunk_id: str
    doc_id: str
    doc_title: str
    section: str | None
    page: int
    text: str
    score: float  # higher = more similar; document the scale you use


def retrieve(question: str, index, model, top_k: int) -> list[RetrievedChunk]:
    """Embed the question with the SAME model as the index and return the top-k chunks."""
    # TODO: embed the question
    # TODO: query the index for top_k results
    # TODO: convert distances to a similarity score (be explicit about the formula)
    # TODO: return results sorted by decreasing score
    ...
