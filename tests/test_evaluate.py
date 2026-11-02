"""Unit tests for the retrieval metrics. Small hand-computed cases only."""

import pytest

from evaluate import hit_at_k, is_correct, mean_reciprocal_rank


def test_hit_at_k_counts_question_once_even_with_several_hits():
    assert hit_at_k([[True, True, True], [False, False, False]], k=3) == 0.5


def test_hit_at_k_ignores_hits_beyond_k():
    assert hit_at_k([[False, False, True]], k=2) == 0.0
    assert hit_at_k([[False, False, True]], k=3) == 1.0


def test_mrr_uses_first_correct_rank():
    assert mean_reciprocal_rank([[False, True, True]]) == 0.5
    assert mean_reciprocal_rank([[True], [False, True]]) == pytest.approx(0.75)


def test_mrr_is_zero_without_correct_chunk():
    assert mean_reciprocal_rank([[False, False]]) == 0.0


def test_is_correct_requires_document_and_page():
    question = {"expected_doc_id": "doc_a", "expected_pages": [14, 15]}
    assert is_correct({"doc_id": "doc_a", "page": 15}, question)
    assert not is_correct({"doc_id": "doc_a", "page": 16}, question)
    assert not is_correct({"doc_id": "doc_b", "page": 15}, question)
