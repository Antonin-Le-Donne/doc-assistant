"""Retrieval evaluation on eval/questions.jsonl.

Usage: python scripts/evaluate.py [--top-k 5] [--label baseline]
Writes eval/results/<label>.json (per-question detail + aggregate metrics).
"""

import argparse
import json
from pathlib import Path
from statistics import mean

from rag_assistant.config import load_settings
from rag_assistant.index import load_embedding_model, open_index
from rag_assistant.retrieve import retrieve

EVAL_DIR = Path("eval")


def is_correct(chunk: dict, question: dict) -> bool:
    """A retrieved chunk is correct if it comes from the expected document AND page."""
    return chunk["doc_id"] == question["expected_doc_id"] and chunk["page"] in question["expected_pages"]


def hit_at_k(ranked_correctness: list[list[bool]], k: int) -> float:
    """Share of questions with at least one correct chunk in the first k."""
    if not ranked_correctness:
        return 0.0
    return sum(any(ranks[:k]) for ranks in ranked_correctness) / len(ranked_correctness)


def mean_reciprocal_rank(ranked_correctness: list[list[bool]]) -> float:
    """Mean of 1/rank of the first correct chunk (0 when there is none)."""
    if not ranked_correctness:
        return 0.0
    return sum(_reciprocal_rank(ranks) for ranks in ranked_correctness) / len(ranked_correctness)


def _reciprocal_rank(ranks: list[bool]) -> float:
    return next((1 / rank for rank, correct in enumerate(ranks, start=1) if correct), 0.0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-k", type=int, default=None, help="default: TOP_K from the settings")
    parser.add_argument("--label", default="baseline", help="name of the results file")
    args = parser.parse_args()

    settings = load_settings()
    top_k = args.top_k or settings.top_k
    index = open_index(settings.index_dir, settings.embedding_model)
    model = load_embedding_model(settings.embedding_model)
    lines = (EVAL_DIR / "questions.jsonl").read_text(encoding="utf-8").splitlines()
    questions = [json.loads(line) for line in lines if line.strip()]

    # Unanswerable questions only record scores: hit@k and MRR ignore them.
    details = []
    for question in questions:
        chunks = retrieve(question["question"], index, model, top_k)
        ranks = [is_correct(chunk, question) for chunk in chunks]
        details.append(
            {
                **question,
                "rank": next((rank for rank, correct in enumerate(ranks, start=1) if correct), None),
                "ranks": ranks,
                "best_score": chunks[0]["score"] if chunks else None,
                "retrieved": [
                    {"doc_id": c["doc_id"], "page": c["page"], "score": round(c["score"], 4)} for c in chunks
                ],
            }
        )

    answerable = [row for row in details if row["answerable"]]
    unanswerable = [row for row in details if not row["answerable"]]
    ranked = [row["ranks"] for row in answerable]
    metrics = {f"hit@{k}": hit_at_k(ranked, k) for k in sorted({1, 3, top_k})}
    metrics["mrr"] = mean_reciprocal_rank(ranked)
    metrics["n_answerable"] = len(answerable)
    metrics["n_unanswerable"] = len(unanswerable)
    metrics["mean_best_score_answerable"] = mean(row["best_score"] for row in answerable) if answerable else None
    metrics["mean_best_score_unanswerable"] = (
        mean(row["best_score"] for row in unanswerable) if unanswerable else None
    )

    print(f"{'id':5} {'rank':>4} {'score':>6}  {'expected':38} first retrieved")
    for row in sorted(answerable, key=lambda row: (row["rank"] is None, row["rank"] or 0), reverse=True):
        expected = f"{row['expected_doc_id']} {row['expected_pages']}"
        first = row["retrieved"][0] if row["retrieved"] else {}
        rank = row["rank"] if row["rank"] is not None else "MISS"
        print(f"{row['id']:5} {rank:>4} {row['best_score']:6.3f}  {expected:38} {first.get('doc_id')} p{first.get('page')}")
    print("\nUnanswerable (scores only):")
    for row in unanswerable:
        first = row["retrieved"][0] if row["retrieved"] else {}
        print(f"{row['id']:5} {row['best_score']:6.3f}  {first.get('doc_id')} p{first.get('page')}")
    print()
    for name, value in metrics.items():
        print(f"{name}: {value:.3f}" if isinstance(value, float) else f"{name}: {value}")

    results_path = EVAL_DIR / "results" / f"{args.label}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "embedding_model": settings.embedding_model,
        "top_k": top_k,
    }
    results_path.write_text(
        json.dumps({"config": config, "metrics": metrics, "questions": details}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nSaved to {results_path}")


if __name__ == "__main__":
    main()
