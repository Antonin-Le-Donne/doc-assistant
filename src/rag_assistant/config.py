"""Settings loaded once from the environment (.env). See SPEC.md §6."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """All tunable values of the pipeline, in one immutable object."""

    data_dir: Path
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    top_k: int
    llm_provider: str  # "ollama" or "api"
    # TODO: add the remaining fields from .env.example (Ollama URL/model, API model/key)


def load_settings() -> Settings:
    """Read .env and environment variables, validate them, return Settings.

    Must fail loudly (clear error message) when a required value is missing
    or invalid, e.g. chunk_overlap >= chunk_size, unknown llm_provider.
    """
    # TODO: load .env with python-dotenv
    # TODO: read each variable, convert types, apply defaults from SPEC.md
    # TODO: validate cross-field rules and raise a ValueError with a clear message
    ...
