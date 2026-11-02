# RAG Doc Assistant

> **Work in progress.** Retrieval is measured below. The `/ask` endpoint has only
> been tested with a fake LLM so far, not with a real model.

A question-answering API over a corpus of technical PDF documents, built with
retrieval-augmented generation (RAG). Every answer cites the document, section
and page it comes from, and retrieval quality is measured on a reference
question set committed before the first retrieval run.

## Why this project

Most RAG demos show a chat window. This one focuses on what makes a document
assistant trustworthy:

- **Traceability**: each answer returns its sources (document, section, page).
- **Measurement**: retrieval is evaluated with hit@k and MRR on a reference set
  written before looking at the results, including questions the corpus cannot
  answer.
- **Honest refusal**: when the retrieved context does not support an answer,
  the API says so instead of inventing one.
- **Local or hosted LLM**: the same pipeline runs with a local model (Ollama,
  LM Studio) or any OpenAI-compatible API.

## Architecture

```
PDF → text per page + metadata → chunks → embeddings + vector store
    → top-k retrieval → LLM answer grounded in retrieved chunks → FastAPI /ask
```

Details in [SPEC.md](SPEC.md).

## Stack

Python · FastAPI · Pydantic · PyMuPDF · sentence-transformers · Chroma ·
Ollama or an OpenAI-compatible LLM API · pytest

## Status

| Stage | Status |
|---|---|
| Corpus selection | ✅ |
| PDF extraction with metadata | ✅ |
| Chunking + indexing | ✅ |
| Retrieval evaluation (hit@k, MRR) | ✅ |
| `/ask` endpoint with cited sources | 🟡 tested with a fake LLM only |
| Configuration comparison | ⏳ |

## Results

Baseline on 21 answerable questions: 1000-character chunks, 150 overlap,
`intfloat/multilingual-e5-base`, top 5.
Per-question detail in [eval/results/baseline.json](eval/results/baseline.json).

| Metric | Value |
|---|---|
| hit@1 | 0.476 |
| hit@3 | 0.571 |
| hit@5 | 0.667 |
| MRR | 0.543 |

What these numbers show:

- **The right document, often the wrong page.** The top chunk comes from the
  expected guide for all 21 questions; the 7 misses are about the page.
- **Lists and tables retrieve poorly.** Exact-value questions fail on the
  `sysctl` list (q20) and the prerequisite table (q04), although the chunk
  holding the answer exists.
- **Scores cannot detect unanswerable questions.** The mean best score is 0.862
  for answerable questions and 0.857 for unanswerable ones, so a score threshold
  would not work with this setup. Refusal relies on the LLM for now.
- **Cross-section questions are flattered.** One chunk from either expected page
  counts as a hit, so q24 can score without retrieving both sections.

## Limitations (v1)

- Text only: images and figures in the PDFs are not processed.
- Small corpus (5–8 documents), chosen for manual evaluation.
- Single user, no authentication.
- `section` is approximate on pages holding several headings; `page` is the
  precise citation.
- The reference questions were drafted with an AI assistant, then committed
  before any retrieval code existed.

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
Copy-Item .env.example .env   # then fill in the values

python scripts/download_corpus.py   # PDFs into data/raw/
python scripts/ingest.py            # pages, chunks and vector index
python scripts/evaluate.py --label baseline
pytest
```

Run the commands from the repository root. Changing `EMBEDDING_MODEL`,
`CHUNK_SIZE` or `CHUNK_OVERLAP` requires running `scripts/ingest.py` again.

### Asking questions

`/ask` needs a running LLM. With LM Studio, load a model, run `lms server start`,
then set `LLM_PROVIDER=api` and `LLM_API_MODEL=<model id>` in `.env`.

```powershell
uvicorn rag_assistant.api:app --app-dir src
```

Then open http://localhost:8000/docs.
