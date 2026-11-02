"""Settings loaded once from the environment (.env)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
LLM_PROVIDERS = ("ollama", "api")


@dataclass(frozen=True)
class Settings:
    """All tunable values of the pipeline, in one immutable object."""

    data_dir: Path
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    top_k: int
    llm_provider: str  # "ollama" or "api"
    ollama_url: str
    ollama_model: str
    llm_api_base_url: str
    llm_api_model: str
    llm_api_key: str

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def index_dir(self) -> Path:
        return self.data_dir / "index"


def _read(name: str, default: str = "") -> str:
    """Environment value, with an empty variable treated as unset."""
    return os.getenv(name, "").strip() or default


def _read_int(name: str, default: int) -> int:
    raw = _read(name, str(default))
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from None


def load_settings() -> Settings:
    """Read and validate the settings; raise ValueError on an invalid value.

    LLM model names are checked by get_llm: ingestion and evaluation need no LLM.
    """
    load_dotenv()
    settings = Settings(
        data_dir=Path(_read("DATA_DIR", "data")),
        chunk_size=_read_int("CHUNK_SIZE", 1000),
        chunk_overlap=_read_int("CHUNK_OVERLAP", 150),
        embedding_model=_read("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
        top_k=_read_int("TOP_K", 5),
        llm_provider=_read("LLM_PROVIDER", "ollama"),
        ollama_url=_read("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=_read("OLLAMA_MODEL"),
        llm_api_base_url=_read("LLM_API_BASE_URL", "http://localhost:1234/v1"),
        llm_api_model=_read("LLM_API_MODEL"),
        llm_api_key=_read("LLM_API_KEY"),
    )
    if settings.chunk_size <= 0:
        raise ValueError(f"CHUNK_SIZE must be positive, got {settings.chunk_size}")
    if not 0 < settings.chunk_overlap < settings.chunk_size:
        raise ValueError(
            "CHUNK_OVERLAP must be positive and smaller than CHUNK_SIZE, "
            f"got {settings.chunk_overlap} and {settings.chunk_size}"
        )
    if settings.top_k <= 0:
        raise ValueError(f"TOP_K must be positive, got {settings.top_k}")
    if settings.llm_provider not in LLM_PROVIDERS:
        raise ValueError(f"LLM_PROVIDER must be one of {LLM_PROVIDERS}, got {settings.llm_provider!r}")
    return settings
