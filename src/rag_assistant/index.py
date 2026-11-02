"""Stage 3: chunks → embeddings → persistent vector store."""

from pathlib import Path
from typing import Iterable

from rag_assistant.chunk import Chunk

COLLECTION_NAME = "chunks"
PASSAGE_PREFIX = "passage: "  # asymmetric E5 prefixes, see docs/decisions.md
EMBEDDING_BATCH_SIZE = 32
WRITE_BATCH_SIZE = 500


def load_embedding_model(model_name: str):
    """Load the sentence-transformers model once and return it."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def build_index(chunks: Iterable[Chunk], model, index_dir: Path, model_name: str) -> int:
    """Embed every chunk and store vectors + metadata + text. Return the chunk count.

    Store the embedding model name alongside the index: querying an index
    with a different model must raise an error instead of returning garbage.
    """
    client = _client(index_dir)
    if COLLECTION_NAME in _collection_names(client):
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": model_name},
    )
    chunks = list(chunks)
    for start in range(0, len(chunks), WRITE_BATCH_SIZE):
        batch = chunks[start : start + WRITE_BATCH_SIZE]
        vectors = model.encode(
            [PASSAGE_PREFIX + chunk["text"] for chunk in batch],
            batch_size=EMBEDDING_BATCH_SIZE,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        collection.add(
            ids=[chunk["chunk_id"] for chunk in batch],
            embeddings=vectors.tolist(),
            documents=[chunk["text"] for chunk in batch],
            metadatas=[_metadata(chunk) for chunk in batch],
        )
    return len(chunks)


def open_index(index_dir: Path, expected_model_name: str):
    """Open an existing index and check it was built with `expected_model_name`.

    Raises FileNotFoundError when no index exists, ValueError on a model mismatch.
    """
    client = _client(index_dir)
    if COLLECTION_NAME not in _collection_names(client):
        raise FileNotFoundError(f"no index in {index_dir}: run scripts/ingest.py first")
    collection = client.get_collection(COLLECTION_NAME)
    built_with = (collection.metadata or {}).get("embedding_model")
    if built_with != expected_model_name:
        raise ValueError(
            f"index in {index_dir} was built with {built_with!r} but EMBEDDING_MODEL is "
            f"{expected_model_name!r}: rebuild it with scripts/ingest.py"
        )
    return collection


def _client(index_dir: Path):
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    index_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(index_dir), settings=ChromaSettings(anonymized_telemetry=False))


def _collection_names(client) -> list[str]:
    return [getattr(collection, "name", collection) for collection in client.list_collections()]


def _metadata(chunk: Chunk) -> dict:
    # Chroma rejects None values: a missing section is simply left out.
    metadata = {
        "doc_id": chunk["doc_id"],
        "doc_title": chunk["doc_title"],
        "page": chunk["page"],
    }
    if chunk["section"] is not None:
        metadata["section"] = chunk["section"]
    return metadata
