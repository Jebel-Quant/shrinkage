"""Tests for the cov1para linear shrinkage estimator."""

import numpy as np
import pytest

from shrinkage.linear import cov1para


@pytest.fixture
def rng():
    """Provide a seeded NumPy random generator for reproducible tests."""
    return np.random.default_rng(42)


def test_output_shape(rng):
    """The estimator returns a (p, p) matrix for p-variable input."""
    Y = rng.standard_normal((100, 5))
    result = cov1para(Y)
    assert result.shape == (5, 5)


def test_symmetry(rng):
    """The shrinkage estimator is symmetric."""
    Y = rng.standard_normal((100, 5))
    result = cov1para(Y)
    np.testing.assert_allclose(result, result.T)


def test_positive_semidefinite(rng):
    """The shrinkage estimator is positive semi-definite."""
    Y = rng.standard_normal((100, 5))
    result = cov1para(Y)
    eigenvalues = np.linalg.eigvalsh(result)
    assert np.all(eigenvalues >= -1e-10)


def test_k_none_demeans(rng):
    """k=None demeans the data, matching pre-demeaned input with k=1."""
    Y = rng.standard_normal((50, 3))
    result_default = cov1para(Y)
    Y_demeaned = Y - Y.mean(axis=0)
    result_k1 = cov1para(Y_demeaned, k=1)
    np.testing.assert_allclose(result_default, result_k1)


def test_k0_no_demeaning(rng):
    """k=0 skips demeaning, so the result differs from the demeaned default."""
    Y = rng.standard_normal((50, 3)) + 5.0
    result_k0 = cov1para(Y, k=0)
    result_default = cov1para(Y)
    assert not np.allclose(result_k0, result_default)


def test_k_nan_treated_as_none(rng):
    """A NaN value for k is treated identically to k=None."""
    Y = rng.standard_normal((50, 3))
    result_nan = cov1para(Y, k=float("nan"))
    result_none = cov1para(Y, k=None)
    np.testing.assert_allclose(result_nan, result_none)


def test_known_values():
    """The estimator yields a symmetric PSD matrix of the expected shape."""
    rng = np.random.default_rng(0)
    Y = rng.standard_normal((200, 4))
    result = cov1para(Y)
    assert result.shape == (4, 4)
    assert np.all(np.linalg.eigvalsh(result) >= -1e-10)
    np.testing.assert_allclose(result, result.T)
