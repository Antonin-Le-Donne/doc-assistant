"""Unit tests for the retrieval metrics. Small hand-computed cases only."""

import pytest

# Remove this line when you start writing the tests.
pytestmark = pytest.mark.skip(reason="not implemented yet")



def test_hit_at_k_counts_question_once_even_with_several_hits():
    # TODO
    ...


def test_hit_at_k_ignores_hits_beyond_k():
    # TODO
    ...


def test_mrr_uses_first_correct_rank():
    # TODO: e.g. first correct at rank 2 → 0.5
    ...


def test_mrr_is_zero_without_correct_chunk():
    # TODO
    ...
