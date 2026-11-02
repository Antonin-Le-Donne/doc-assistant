"""Settings: defaults and loud failures on invalid values."""

import pytest

from rag_assistant import config
from rag_assistant.llm import ApiLLM, OllamaLLM, get_llm

VARIABLES = (
    "DATA_DIR", "CHUNK_SIZE", "CHUNK_OVERLAP", "EMBEDDING_MODEL", "TOP_K", "LLM_PROVIDER", "OLLAMA_URL",
    "OLLAMA_MODEL", "LLM_API_BASE_URL", "LLM_API_MODEL", "LLM_API_KEY",
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    for name in VARIABLES:
        monkeypatch.delenv(name, raising=False)


def test_defaults_match_the_spec():
    settings = config.load_settings()
    assert (settings.chunk_size, settings.chunk_overlap, settings.top_k) == (1000, 150, 5)
    assert settings.llm_provider == "ollama"
    assert settings.embedding_model == config.DEFAULT_EMBEDDING_MODEL


@pytest.mark.parametrize(
    "name, value",
    [
        ("CHUNK_OVERLAP", "1000"),
        ("CHUNK_OVERLAP", "0"),
        ("CHUNK_SIZE", "-1"),
        ("CHUNK_SIZE", "abc"),
        ("TOP_K", "0"),
        ("LLM_PROVIDER", "gemini"),
    ],
)
def test_invalid_values_fail_loudly(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError, match=name):
        config.load_settings()


def test_get_llm_requires_a_model_name(monkeypatch):
    with pytest.raises(ValueError, match="OLLAMA_MODEL"):
        get_llm(config.load_settings())
    monkeypatch.setenv("LLM_PROVIDER", "api")
    with pytest.raises(ValueError, match="LLM_API_MODEL"):
        get_llm(config.load_settings())


def test_get_llm_selects_the_provider(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "local-model")
    assert isinstance(get_llm(config.load_settings()), OllamaLLM)
    monkeypatch.setenv("LLM_PROVIDER", "api")
    monkeypatch.setenv("LLM_API_MODEL", "hosted-model")
    llm = get_llm(config.load_settings())
    assert isinstance(llm, ApiLLM)
    assert "Authorization" not in llm.client.headers  # local servers need no key
