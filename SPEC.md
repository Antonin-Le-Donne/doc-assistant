# RAG Doc Assistant — Specification

Source of truth for scope, architecture, definitions and evaluation.
If code and this file disagree, this file wins until it is explicitly changed
(and the change is logged in `docs/decisions.md`).

## 1. Goal

A small, honest prototype of a question-answering assistant over a corpus of
technical PDF documents, built with retrieval-augmented generation (RAG).

The point is not the chat. The point is to **measure** whether the system
retrieves the right passages and to **trace** every answer back to its sources.

Hard deadline: a usable version (evenings 1–4) before **3 November 2026**.
Anything not needed for that is labelled `after-application`.

## 2. Non-goals (v1)

- No user interface. The API and its `/docs` page are the interface.
- No image or figure understanding. Text (and optionally tables) only.
- No agents, no multi-step orchestration.
- No authentication, no multi-user state.
- No fine-tuning of any model.

## 3. Corpus

- 5 to 8 public technical PDF documents, ideally in French.
- Licence checked **before** committing any PDF. If redistribution is not
  allowed, the PDFs are not committed: `scripts/download_corpus.py` fetches them
  from their direct URLs into `data/raw/`.
- `docs/corpus.md` lists every document: title, source URL, licence, page count,
  why it was chosen, known extraction difficulties.

## 4. Architecture

```
PDF files (data/raw/)
   │  extract.py   — text per page + metadata (doc, section, page)
   ▼
Pages (data/processed/pages.jsonl)
   │  chunk.py     — split into overlapping chunks, metadata kept
   ▼
Chunks (data/processed/chunks.jsonl)
   │  index.py     — embeddings + persistent vector store
   ▼
Vector index (data/index/)
   │  retrieve.py  — top-k search for a question
   ▼
Retrieved chunks ──► llm.py — answer generated ONLY from retrieved context
   │
   ▼
api.py — POST /ask → answer + cited sources
```

Each stage writes its output to disk so it can be inspected and re-run alone.

## 5. Data model

### Page
| Field | Type | Notes |
|---|---|---|
| `doc_id` | str | stable slug of the file name |
| `doc_title` | str | from PDF metadata, else first heading, else file name |
| `page` | int | 1-based, as printed by a PDF viewer |
| `section` | str \| null | closest heading above the text on this page |
| `text` | str | cleaned text (repeated headers/footers removed) |

### Chunk
| Field | Type | Notes |
|---|---|---|
| `chunk_id` | str | `{doc_id}:{page}:{n}` |
| `doc_id`, `doc_title`, `section`, `page` | | inherited from the page |
| `text` | str | chunk content |
| `char_count` | int | for sanity checks |

A chunk never spans two documents. Whether a chunk may span two pages is a
decision to log.

## 6. Configuration

All tunable values come from environment variables (see `.env.example`),
loaded once in `config.py`. Starting points, to be tuned and logged:

| Name | Default | Meaning |
|---|---|---|
| `CHUNK_SIZE` | 1000 | characters per chunk |
| `CHUNK_OVERLAP` | 150 | characters shared by consecutive chunks |
| `EMBEDDING_MODEL` | a multilingual sentence-transformers model | must handle French |
| `TOP_K` | 5 | chunks retrieved per question |
| `LLM_PROVIDER` | `ollama` | `ollama` or `api` |

## 7. API contract

### `GET /health`
Returns status and whether the index is loaded.

### `POST /ask`
Request:
```json
{ "question": "string, 3–500 chars", "top_k": 5 }
```
Response:
```json
{
  "answer": "string",
  "sources": [
    { "doc_title": "string", "section": "string|null", "page": 14,
      "score": 0.82, "excerpt": "first ~200 chars of the chunk" }
  ],
  "answered": true
}
```
- `answered` is `false` when the retrieved context does not support an answer.
  The assistant must say so instead of inventing one.
- The index and the embedding model are loaded **once** at startup (FastAPI
  `lifespan`), never per request.

## 8. Evaluation

### Reference set — `eval/questions.jsonl`
One JSON object per line:
```json
{ "id": "q01", "question": "...", "expected_doc_id": "...", "expected_pages": [14, 15], "answerable": true }
```
- 20 to 30 questions.
- Include 3 to 5 questions the corpus cannot answer (`answerable: false`).
- Mix of question types: definition, procedure, specific value, cross-section.

### Retrieval metrics (evening 2 — the most important ones)
- **hit@k**: share of answerable questions where at least one of the top-k
  chunks comes from the expected document AND one of the expected pages.
- **MRR** (mean reciprocal rank): mean of `1 / rank` of the first correct chunk
  (0 if none in top-k).
- Report per question, not only the average: the failures are the findings.

### Comparison (evening 4)
Run the same evaluation on two configurations that differ by **one** variable
(e.g. chunk size 500 vs 1000). Results table in the README.

### Answer quality (after application)
Manual grading of answers on the reference set: correct / partially correct /
wrong / correctly refused; and whether each cited source actually supports the
answer.

## 9. Repository layout

```
.
├── SPEC.md              this file
├── README.md
├── .env.example
├── requirements.txt
├── docs/
│   ├── corpus.md        document list + licences
│   ├── decisions.md     decision log
│   └── eval-reading-plan.md  passages behind the reference questions
├── src/rag_assistant/
│   ├── config.py
│   ├── extract.py
│   ├── chunk.py
│   ├── index.py
│   ├── retrieve.py
│   ├── llm.py
│   ├── schemas.py
│   └── api.py
├── scripts/
│   ├── download_corpus.py
│   ├── ingest.py        extract → chunk → index
│   └── evaluate.py      retrieval metrics on eval/questions.jsonl
├── eval/questions.jsonl
├── tests/
└── data/                git-ignored (raw/, processed/, index/)
```

## 10. Known risks

- **Extraction quality** is the main silent failure: repeated headers, broken
  hyphenation, tables flattened into noise. Inspect `pages.jsonl` by eye on at
  least 3 documents before chunking.
- **Evaluation leakage**: writing the reference questions after seeing what
  retrieval returns makes the score meaningless.
- **Index/model mismatch**: an index built with one embedding model and queried
  with another returns garbage without any error.
- **Scope creep before 3 November**: UI, agents, Docker, reranking all wait.
