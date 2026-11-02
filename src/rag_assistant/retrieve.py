"""Stage 4: question → top-k chunks with scores."""

from typing import TypedDict

QUERY_PREFIX = "query: "  # expected by E5 models


class RetrievedChunk(TypedDict):
    chunk_id: str
    doc_id: str
    doc_title: str
    section: str | None
    page: int
    text: str
    score: float  # cosine similarity (1 - distance)


def retrieve(question: str, index, model, top_k: int) -> list[RetrievedChunk]:
    """Embed the question with the SAME model as the index and return the top-k chunks."""
    vector = model.encode(QUERY_PREFIX + question, normalize_embeddings=True, show_progress_bar=False)
    results = index.query(
        query_embeddings=[vector.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = [
        RetrievedChunk(
            chunk_id=chunk_id,
            doc_id=metadata["doc_id"],
            doc_title=metadata["doc_title"],
            section=metadata.get("section"),
            page=metadata["page"],
            text=text,
            score=1.0 - distance,
        )
        for chunk_id, text, metadata, distance in zip(
            results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]
    return sorted(chunks, key=lambda chunk: chunk["score"], reverse=True)
