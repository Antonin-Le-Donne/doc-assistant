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
| 2026-11-02 | No relevance threshold in v1: the LLM's refusal marker alone sets `answered: false`, and `/ask` logs the retrieval scores. Revisit after measuring. | Pick an arbitrary score threshold now; an optional threshold disabled by default. | Absolute scores depend on the model, corpus and chunking, and a high similarity score alone does not prove that a passage answers the question. Relying on the LLM is a known weakness until scores for answerable and unanswerable questions justify a threshold. |
| 2026-11-02 | LLM: stay free and local for now, undecided on the final model. Keep `OllamaLLM` and make `ApiLLM` a generic OpenAI-compatible chat client, with `LLM_API_BASE_URL` defaulting to LM Studio's local server. | OpenAI Responses API with `gpt-6.1-terra` (initial choice, dropped: paid API, not covered by a ChatGPT subscription); Ollama only. | One client covers LM Studio, OpenRouter, Hugging Face and OpenAI, so changing provider is a `.env` change. The key stays in local `.env` as `LLM_API_KEY`, never in source code or Git. |
| 2026-11-02 | Reference set target: 25 questions, five per PDF, including four unanswerable questions. Drafted by Claude and committed before any retrieval code existed. | Larger set; answerable questions only; written by hand. | 25 is within the 20–30 range in `SPEC.md` §8 and gives every guide equal coverage. The unanswerable cases test refusal rather than unsupported completion. What protects against leakage is the order (questions first, results after), so it is the claim the README makes. |
| 2026-11-02 | Expected pages use the 1-based PDF-viewer page number. | Printed footer page number. | Covers and front matter create offsets. One convention must be used in `Page.page`, `Chunk.page`, API sources and `expected_pages`. |
| 2026-11-02 | `/ask` returns all retrieved chunks as `sources`, in rank order, and none on a refusal. | Return only the chunks cited in the answer. | Keeps `[n]` in the answer mapped to `sources[n-1]` without parsing the model's output. A source being listed therefore does not prove it was used; checking that is the after-application grading in `SPEC.md` §8. |
| 2026-11-02 | `top_k` is optional in `/ask` (1–20); when omitted, `TOP_K` from the settings applies. | Fixed default of 5 in the request schema. | A fixed default would silently ignore `TOP_K`. The API contract still accepts the same requests. |
| 2026-11-02 | Page `section` is the last heading found on or before the page, detected by font size (at least 1.35× the body size) and a leading number, roman numeral or "Annexe". | PDF bookmarks; font size alone (recommendation titles and callouts then pass as sections). | The hygiene guide has no bookmarks, and a single method keeps all five guides comparable. A page holding several headings is labelled with its last one, so `section` is approximate; `page` remains the precise citation. |

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
