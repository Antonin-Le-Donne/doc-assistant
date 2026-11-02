"""LLM access behind one interface, so local and hosted models are interchangeable."""

from typing import Protocol

from rag_assistant.retrieve import RetrievedChunk


class LLM(Protocol):
    def generate(self, prompt: str) -> str:
        """Return the model's text completion for `prompt`."""
        ...


class OllamaLLM:
    """Local model served by Ollama (no API key)."""

    def __init__(self, base_url: str, model: str) -> None:
        # TODO: store settings, create an HTTP client with a sensible timeout
        ...

    def generate(self, prompt: str) -> str:
        # TODO: call the Ollama generate endpoint, return the text, raise on HTTP errors
        ...


class ApiLLM:
    """Hosted model through a provider API (key read from settings, never hard-coded)."""

    def __init__(self, model: str, api_key: str) -> None:
        # TODO
        ...

    def generate(self, prompt: str) -> str:
        # TODO
        ...


def get_llm(settings) -> LLM:
    """Factory: return OllamaLLM or ApiLLM according to settings.llm_provider."""
    # TODO
    ...


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Prompt that forces answers grounded in the chunks, with numbered sources.

    The model must: answer only from the provided context, cite sources by
    number, and reply with an explicit refusal marker when the context does
    not contain the answer (so `answered` can be set to False).
    """
    # TODO: number each chunk and include doc_title / section / page
    # TODO: write the instructions (grounding, citations, refusal marker)
    ...
