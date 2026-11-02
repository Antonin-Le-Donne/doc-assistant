# RAG Doc Assistant

> **Work in progress.** Results and usage instructions will be added as the
> project is built. Nothing below claims results that do not exist yet.

A question-answering API over a corpus of technical PDF documents, built with
retrieval-augmented generation (RAG). Every answer cites the document, section
and page it comes from, and retrieval quality is measured on a hand-written
reference question set.

## Why this project

Most RAG demos show a chat window. This one focuses on what makes a document
assistant trustworthy:

- **Traceability**: each answer returns its sources (document, section, page).
- **Measurement**: retrieval is evaluated with hit@k and MRR on a reference set
  written before looking at the results, including questions the corpus cannot
  answer.
- **Honest refusal**: when the retrieved context does not support an answer,
  the API says so instead of inventing one.
- **Local or hosted LLM**: the same pipeline runs with a local model (Ollama)
  or a hosted API, which makes the two comparable.

## Planned architecture

```
PDF → text per page + metadata → chunks → embeddings + vector store
    → top-k retrieval → LLM answer grounded in retrieved chunks → FastAPI /ask
```

Details in [SPEC.md](SPEC.md).

## Stack

Python · FastAPI · Pydantic · PyMuPDF · sentence-transformers · Chroma ·
Ollama or a hosted LLM API · pytest

## Status

| Stage | Status |
|---|---|
| Corpus selection | ⏳ |
| PDF extraction with metadata | ⏳ |
| Chunking + indexing | ⏳ |
| Retrieval evaluation (hit@k, MRR) | ⏳ |
| `/ask` endpoint with cited sources | ⏳ |
| Configuration comparison | ⏳ |

## Results

_Coming soon: retrieval metrics table, example question with sources._

## Limitations (v1)

- Text only: images and figures in the PDFs are not processed.
- Small corpus (5–8 documents), chosen for manual evaluation.
- Single user, no authentication.

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
Copy-Item .env.example .env   # then fill in the values
```