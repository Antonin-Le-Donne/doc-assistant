"""FastAPI app: GET /health, POST /ask. See SPEC.md §7.

Run (from the repo root, venv active):
    uvicorn rag_assistant.api:app --reload --app-dir src
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_assistant.schemas import AskRequest, AskResponse, HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load settings, embedding model, index and LLM ONCE, at startup."""
    # TODO: load settings
    # TODO: load the embedding model and open the index (check model name)
    # TODO: build the LLM with get_llm
    # TODO: store them on app.state
    yield
    # TODO: release resources if needed


app = FastAPI(title="RAG Doc Assistant", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    # TODO
    ...


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Retrieve, build the prompt, generate, map chunks to Sources."""
    # TODO: retrieve top_k chunks
    # TODO: decide what happens when no chunk is relevant enough (threshold? log it)
    # TODO: build the prompt, call the LLM, detect the refusal marker
    # TODO: return answer + sources + answered
    ...
