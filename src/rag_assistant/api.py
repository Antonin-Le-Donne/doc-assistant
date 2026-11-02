"""FastAPI app: GET /health, POST /ask.

Run (from the repo root, venv active):
    uvicorn rag_assistant.api:app --reload --app-dir src
"""

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

from rag_assistant.config import load_settings
from rag_assistant.index import load_embedding_model, open_index
from rag_assistant.llm import build_prompt, get_llm, is_refusal
from rag_assistant.retrieve import RetrievedChunk, retrieve
from rag_assistant.schemas import AskRequest, AskResponse, HealthResponse, Source

logger = logging.getLogger("uvicorn.error")

REFUSAL_ANSWER = "Les documents disponibles ne permettent pas de répondre à cette question."
EXCERPT_LENGTH = 200


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load settings, embedding model, index and LLM ONCE, at startup."""
    settings = load_settings()
    app.state.settings = settings
    app.state.llm = get_llm(settings)
    try:
        app.state.index = open_index(settings.index_dir, settings.embedding_model)
        app.state.model = load_embedding_model(settings.embedding_model)
    except FileNotFoundError as error:
        # Reported by /health; a model mismatch (ValueError) still stops the startup.
        logger.error("%s", error)
        app.state.index = None
        app.state.model = None
    yield
    app.state.llm.close()


app = FastAPI(title="RAG Doc Assistant", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    state = request.app.state
    loaded = state.index is not None
    return HealthResponse(
        status="ok" if loaded else "degraded",
        index_loaded=loaded,
        chunk_count=state.index.count() if loaded else 0,
        embedding_model=state.settings.embedding_model,
        llm_provider=state.settings.llm_provider,
    )


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, request: Request) -> AskResponse:
    """Retrieve, build the prompt, generate, map chunks to Sources.

    No relevance threshold yet: the LLM's refusal marker decides, and scores are logged.
    """
    state = request.app.state
    if state.index is None:
        raise HTTPException(status_code=503, detail="Index not loaded: run scripts/ingest.py")

    top_k = body.top_k or state.settings.top_k
    chunks = retrieve(body.question, state.index, state.model, top_k)
    logger.info("ask top_k=%d scores=%s", top_k, [round(chunk["score"], 3) for chunk in chunks])
    if not chunks:
        return AskResponse(answer=REFUSAL_ANSWER, sources=[], answered=False)

    try:
        answer = state.llm.generate(build_prompt(body.question, chunks))
    except httpx.HTTPError as error:
        logger.error("LLM call failed: %r", error)
        raise HTTPException(status_code=503, detail="LLM unavailable") from error

    if is_refusal(answer):
        logger.info("ask refused best_score=%.3f", chunks[0]["score"])
        return AskResponse(answer=REFUSAL_ANSWER, sources=[], answered=False)
    # Same order as the prompt: "[n]" in the answer is sources[n-1].
    return AskResponse(answer=answer.strip(), sources=[_to_source(chunk) for chunk in chunks], answered=True)


def _to_source(chunk: RetrievedChunk) -> Source:
    return Source(
        doc_title=chunk["doc_title"],
        section=chunk["section"],
        page=chunk["page"],
        score=round(chunk["score"], 4),
        excerpt=" ".join(chunk["text"].split())[:EXCERPT_LENGTH],
    )
