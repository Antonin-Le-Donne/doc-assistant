# Decision log

Record each non-obvious choice with a short rationale. `SPEC.md` remains the
source of truth for scope and contracts.

| Date | Decision | Alternatives considered | Why |
|---|---|---|---|
| 2026-10-27 | Measure retrieval (hit@k, MRR) before integrating the LLM. | Evaluate only final answers. | If the right passage is not retrieved, the LLM cannot repair retrieval. Measuring first isolates the failure. |
| 2026-11-02 | Embeddings: `intfloat/multilingual-e5-base`. Use `query: ` for questions and `passage: ` for chunks. | English-only model; larger multilingual model. | The corpus and questions are French. E5 is multilingual and uses asymmetric query/passage prefixes. Keep the model identical at indexing and query time. |
| 2026-11-02 | Vector store: persistent Chroma with cosine distance. | In-memory index; another vector database. | Chroma is already in the scaffold dependencies and its local persistence fits this small corpus. Store the embedding model name with the collection to detect mismatches. |
| 2026-11-02 | Initial chunk settings: `CHUNK_SIZE=1000` characters and `CHUNK_OVERLAP=150` characters. | 500/1000/1500 characters; no overlap. | These are the starting values in `SPEC.md` §6. The unit is characters, not tokens. Compare 500 vs 1000 while keeping overlap fixed at 150. |
| 2026-11-02 | Chunks never cross PDF page boundaries. | Merge the end of one page with the next. | A single page per chunk keeps citations precise and makes `expected_pages`, hit@k and MRR unambiguous. |
| 2026-11-02 | Enforce a hard chunk-length limit; split oversized paragraphs further. | Accumulate paragraphs without a strict upper bound. | A paragraph may exceed the target by itself. Every emitted chunk must satisfy `len(text) <= CHUNK_SIZE`; overlap is in characters, positive and smaller than the size. Splitting must always make progress and must not emit empty chunks. |
| 2026-11-02 | Do not fix a relevance threshold before measuring a baseline. | Pick an arbitrary score threshold; trust the LLM alone. | Absolute scores depend on the model, corpus and chunking. Record scores for answerable and unanswerable questions first. A high similarity score alone does not prove that a passage answers the question. |
| 2026-11-02 | Hosted LLM option: OpenAI Responses API; keep the model configurable (`gpt-6.1-terra` as an initial candidate). Keep Ollama as the local alternative. | Ollama only; legacy Assistants API. | A hosted model avoids a local LLM installation. Responses is the API to use for a new integration; the Assistants API was retired on 2026-08-26. Store the key in local `.env` as `LLM_API_KEY`, never in source code or Git. |
| 2026-11-02 | Reference set target: 25 questions, five per PDF, including four unanswerable questions. | Larger set; answerable questions only. | 25 is within the 20–30 range in `SPEC.md` §8 and gives every guide equal coverage. The unanswerable cases test refusal rather than unsupported completion. Write the set before inspecting retrieval results. |
| 2026-11-02 | Expected pages use the 1-based PDF-viewer page number. | Printed footer page number. | Covers and front matter create offsets. One convention must be used in `Page.page`, `Chunk.page`, API sources and `expected_pages`. |

## Configuration rules

- Changing `EMBEDDING_MODEL` requires rebuilding the index.
- `CHUNK_SIZE` and `CHUNK_OVERLAP` must be positive, with overlap strictly
  smaller than chunk size.
- Chunk size and overlap are measured in characters, even though embedding
  models process tokens.
- Put the API key in a local `.env` copied from `.env.example`, under
  `LLM_API_KEY`. Never put it in a Python comment, `config.py`, README or Git.
- Model and threshold choices are starting points, not measured results. Revisit
  them after the first evaluation.
