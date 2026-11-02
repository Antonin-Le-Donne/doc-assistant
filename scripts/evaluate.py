"""Retrieval evaluation on eval/questions.jsonl. See SPEC.md §8.

Usage: python scripts/evaluate.py [--top-k 5] [--label baseline]
Writes eval/results/<label>.json (per-question detail + aggregate metrics).
"""


def is_correct(chunk: dict, question: dict) -> bool:
    """A retrieved chunk is correct if it comes from the expected document AND page."""
    # TODO
    ...


def hit_at_k(ranked_correctness: list[list[bool]], k: int) -> float:
    """Share of questions with at least one correct chunk in the first k."""
    # TODO
    ...


def mean_reciprocal_rank(ranked_correctness: list[list[bool]]) -> float:
    """Mean of 1/rank of the first correct chunk (0 when there is none)."""
    # TODO
    ...


def main() -> None:
    # TODO: parse arguments
    # TODO: load questions; evaluate only answerable ones for hit@k / MRR
    # TODO: retrieve for each question, compute correctness per rank
    # TODO: print a per-question table (misses first) and the aggregates
    # TODO: save results with the config used (chunk size, overlap, model, top_k)
    ...


if __name__ == "__main__":
    main()
