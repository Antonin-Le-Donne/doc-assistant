"""API tests with FastAPI's TestClient. The LLM is replaced by a fake: tests must
not depend on a running model or on network access."""

import pytest

# Remove this line when you start writing the tests.
pytestmark = pytest.mark.skip(reason="not implemented yet")



class FakeLLM:
    """Returns a fixed answer so tests are deterministic."""

    def generate(self, prompt: str) -> str:
        # TODO: return a canned answer (and a refusal variant for another test)
        ...


def test_health_reports_index_loaded():
    # TODO
    ...


def test_ask_returns_answer_and_sources():
    # TODO: sources carry doc_title, page, score, excerpt
    ...


def test_ask_rejects_invalid_question():
    # TODO: empty / too long question → 422
    ...


def test_ask_refusal_sets_answered_false():
    # TODO
    ...
