"""API tests with FastAPI's TestClient. The LLM is replaced by a fake: tests must
not depend on a running model or on network access."""

from dataclasses import dataclass

import httpx
import pytest
from fastapi.testclient import TestClient

from rag_assistant import api
from rag_assistant.llm import REFUSAL_MARKER


class FakeLLM:
    """Returns a fixed answer so tests are deterministic."""

    def __init__(self, answer: str = "Le port est TCP/502 [1].", error: Exception | None = None) -> None:
        self.answer = answer
        self.error = error

    def generate(self, prompt: str) -> str:
        if self.error:
            raise self.error
        return self.answer

    def close(self) -> None:
        pass


class FakeIndex:
    def count(self) -> int:
        return 1


@dataclass(frozen=True)
class FakeSettings:
    index_dir: str = "unused"
    embedding_model: str = "fake-model"
    llm_provider: str = "ollama"
    top_k: int = 3


CHUNK = {
    "chunk_id": "doc:66:0",
    "doc_id": "doc",
    "doc_title": "Guide industriel",
    "section": "4.2.2 Cloisonnement",
    "page": 66,
    "text": "Modbus : TCP/502. " * 30,
    "score": 0.82,
}


def make_client(monkeypatch, llm=None, index=FakeIndex(), chunks=(CHUNK,)) -> TestClient:
    monkeypatch.setattr(api, "load_settings", FakeSettings)
    monkeypatch.setattr(api, "get_llm", lambda settings: llm or FakeLLM())
    monkeypatch.setattr(api, "load_embedding_model", lambda name: object())

    def open_index(index_dir, model_name):
        if index is None:
            raise FileNotFoundError("no index")
        return index

    monkeypatch.setattr(api, "open_index", open_index)
    monkeypatch.setattr(api, "retrieve", lambda question, index, model, top_k: list(chunks)[:top_k])
    return TestClient(api.app)


def test_health_reports_index_loaded(monkeypatch):
    with make_client(monkeypatch) as client:
        body = client.get("/health").json()
    assert body == {
        "status": "ok",
        "index_loaded": True,
        "chunk_count": 1,
        "embedding_model": "fake-model",
        "llm_provider": "ollama",
    }


def test_health_and_ask_without_index(monkeypatch):
    with make_client(monkeypatch, index=None) as client:
        assert client.get("/health").json()["index_loaded"] is False
        assert client.post("/ask", json={"question": "Quel port ?"}).status_code == 503


def test_model_mismatch_stops_startup(monkeypatch):
    make_client(monkeypatch)

    def mismatch(index_dir, model_name):
        raise ValueError("model mismatch")

    monkeypatch.setattr(api, "open_index", mismatch)
    with pytest.raises(ValueError, match="model mismatch"):
        with TestClient(api.app):
            pass


def test_ask_returns_answer_and_sources(monkeypatch):
    with make_client(monkeypatch) as client:
        response = client.post("/ask", json={"question": "Quel port pour Modbus ?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answered"] is True
    assert body["answer"] == "Le port est TCP/502 [1]."
    source = body["sources"][0]
    assert source["doc_title"] == "Guide industriel"
    assert source["section"] == "4.2.2 Cloisonnement"
    assert source["page"] == 66
    assert source["score"] == 0.82
    assert source["excerpt"].startswith("Modbus : TCP/502.")
    assert len(source["excerpt"]) <= 200


@pytest.mark.parametrize(
    "payload",
    [
        {"question": ""},
        {"question": "  a "},
        {"question": "x" * 501},
        {"question": "Quel port ?", "top_k": 0},
        {"question": "Quel port ?", "top_k": 21},
    ],
)
def test_ask_rejects_invalid_question(monkeypatch, payload):
    with make_client(monkeypatch) as client:
        assert client.post("/ask", json=payload).status_code == 422


def test_ask_refusal_sets_answered_false(monkeypatch):
    with make_client(monkeypatch, llm=FakeLLM(answer=f" {REFUSAL_MARKER} ")) as client:
        body = client.post("/ask", json={"question": "Quel délai sous NIS2 ?"}).json()
    assert body["answered"] is False
    assert body["sources"] == []
    assert REFUSAL_MARKER not in body["answer"]


def test_ask_without_chunk_does_not_call_the_llm(monkeypatch):
    llm = FakeLLM(error=AssertionError("the LLM must not be called"))
    with make_client(monkeypatch, llm=llm, chunks=()) as client:
        assert client.post("/ask", json={"question": "Quel port ?"}).json()["answered"] is False


def test_ask_reports_unavailable_llm(monkeypatch):
    llm = FakeLLM(error=httpx.ConnectError("connection refused"))
    with make_client(monkeypatch, llm=llm) as client:
        assert client.post("/ask", json={"question": "Quel port ?"}).status_code == 503
