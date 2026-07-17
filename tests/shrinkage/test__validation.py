"""Tests for the shared input-validation helpers."""

import numpy as np
import pytest

from shrinkage._validation import effective_sample_size, validate_observation_matrix


def test_valid_matrix_returns_shape():
    """A well-formed (N, p) matrix passes and its shape is returned."""
    Y = np.zeros((7, 3))
    assert validate_observation_matrix(Y) == (7, 3)


@pytest.mark.parametrize(
    ("Y", "match"),
    [
        (np.zeros(4), "2-D"),
        (np.zeros((2, 2, 2)), "2-D"),
        (np.zeros((4, 0)), "at least one variable"),
        (np.zeros((0, 4)), "at least one observation"),
        (np.array([[np.nan, 0.0], [1.0, 2.0]]), "finite"),
        (np.array([[np.inf, 0.0], [1.0, 2.0]]), "finite"),
    ],
)
def test_invalid_matrix_raises(Y, match):
    """Each degenerate matrix raises ValueError naming the offending condition."""
    with pytest.raises(ValueError, match=match):
        validate_observation_matrix(Y)


def test_effective_sample_size_positive():
    """A positive effective sample size is returned unchanged."""
    assert effective_sample_size(10, 1) == 9


@pytest.mark.parametrize("k", [10, 11])
def test_effective_sample_size_non_positive_raises(k):
    """N = N - k <= 0 raises ValueError naming the effective sample size."""
    with pytest.raises(ValueError, match="Effective sample size"):
        effective_sample_size(10, k)
