"""LLM access behind one interface, so local and hosted models are interchangeable."""

from typing import Protocol

import httpx

from rag_assistant.retrieve import RetrievedChunk

REFUSAL_MARKER = "[SANS_REPONSE]"
LLM_TIMEOUT_SECONDS = 300.0  # local models can be slow


class LLM(Protocol):
    def generate(self, prompt: str) -> str:
        """Return the model's text completion for `prompt`."""
        ...

    def close(self) -> None:
        """Release the underlying HTTP client."""
        ...


class OllamaLLM:
    """Local model served by Ollama (no API key)."""

    def __init__(self, base_url: str, model: str) -> None:
        self.model = model
        self.client = httpx.Client(base_url=base_url, timeout=LLM_TIMEOUT_SECONDS)

    def generate(self, prompt: str) -> str:
        response = self.client.post(
            "/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0}},
        )
        response.raise_for_status()
        return response.json()["response"]

    def close(self) -> None:
        self.client.close()


class ApiLLM:
    """Any OpenAI-compatible chat API. Local servers need no key."""

    def __init__(self, model: str, api_key: str, base_url: str) -> None:
        self.model = model
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.Client(base_url=base_url.rstrip("/") + "/", headers=headers, timeout=LLM_TIMEOUT_SECONDS)

    def generate(self, prompt: str) -> str:
        response = self.client.post(
            "chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def close(self) -> None:
        self.client.close()


def get_llm(settings) -> LLM:
    """Factory: return OllamaLLM or ApiLLM according to settings.llm_provider."""
    if settings.llm_provider == "ollama":
        if not settings.ollama_model:
            raise ValueError("LLM_PROVIDER=ollama requires OLLAMA_MODEL")
        return OllamaLLM(settings.ollama_url, settings.ollama_model)
    if settings.llm_provider == "api":
        if not settings.llm_api_model:
            raise ValueError("LLM_PROVIDER=api requires LLM_API_MODEL")
        return ApiLLM(settings.llm_api_model, settings.llm_api_key, settings.llm_api_base_url)
    raise ValueError(f"unknown LLM provider: {settings.llm_provider!r}")


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Prompt asking for an answer from the chunks only, or the refusal marker."""
    context = "\n\n".join(
        f"[{number}] {chunk['doc_title']} — section : {chunk['section'] or 'inconnue'} — page {chunk['page']}\n"
        f"{chunk['text']}"
        for number, chunk in enumerate(chunks, start=1)
    )
    return (
        "Tu réponds à des questions techniques à partir d'extraits de guides de sécurité.\n"
        "Règles :\n"
        "- Réponds en français, uniquement à partir des extraits ci-dessous, sans connaissance extérieure.\n"
        "- Cite chaque information avec le numéro de son extrait, par exemple [1].\n"
        "- Si les extraits ne permettent pas de répondre à la question, "
        f"réponds exactement {REFUSAL_MARKER} et rien d'autre.\n\n"
        f"Extraits :\n{context}\n\n"
        f"Question : {question}\n"
        "Réponse :"
    )


def is_refusal(answer: str) -> bool:
    """True when the model used the refusal marker anywhere in its answer."""
    return REFUSAL_MARKER in answer
