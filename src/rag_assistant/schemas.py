"""Pydantic models for the API contract. See SPEC.md §7."""

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=3, max_length=500)
    top_k: int | None = Field(default=None, ge=1, le=20)  # None = TOP_K from the settings


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
    chunk_count: int
    embedding_model: str
    llm_provider: str
