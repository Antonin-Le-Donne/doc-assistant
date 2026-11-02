"""Stage 3: chunks → embeddings → persistent vector store."""

from pathlib import Path
from typing import Iterable

from rag_assistant.chunk import Chunk


def load_embedding_model(model_name: str):
    """Load the sentence-transformers model once and return it."""
    # TODO
    ...


def build_index(chunks: Iterable[Chunk], model, index_dir: Path, model_name: str) -> int:
    """Embed every chunk and store vectors + metadata + text. Return the chunk count.

    Store the embedding model name alongside the index: querying an index
    with a different model must raise an error instead of returning garbage.
    """
    # TODO: create (or reset) a persistent collection in index_dir
    # TODO: embed chunk texts in batches
    # TODO: add ids, vectors, documents and metadata (doc_id, doc_title, section, page)
    # TODO: record model_name in the collection metadata
    ...


def open_index(index_dir: Path, expected_model_name: str):
    """Open an existing index and check it was built with `expected_model_name`."""
    # TODO
    ...
