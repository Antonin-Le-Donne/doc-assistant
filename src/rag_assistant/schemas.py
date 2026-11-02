"""Pydantic models for the API contract. See SPEC.md §7."""

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str  # TODO: enforce 3–500 characters with Field constraints
    top_k: int = 5  # TODO: enforce a sensible range


class Source(BaseModel):
    doc_title: str
    section: str | None
    page: int
    score: float
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    answered: bool


class HealthResponse(BaseModel):
    status: str
    index_loaded: bool
    # TODO: chunk count, embedding model name, LLM provider
