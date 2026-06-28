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


def _reference_cov1para(Y: np.ndarray, k: int | None = None) -> np.ndarray:
    """Independent re-implementation of the Ledoit-Wolf one-parameter estimator.

    Mirrors the published formula directly so the test pins the production code
    to a numerical reference rather than only to structural invariants.
    """
    N, p = Y.shape
    if k is None or (isinstance(k, float) and np.isnan(k)):
        Y = Y - Y.mean(axis=0)
        k = 1
    n = N - k
    sample = (Y.T @ Y) / n
    mu = np.trace(sample) / p
    target = mu * np.eye(p)
    Y2 = Y**2
    pi_hat = np.sum((Y2.T @ Y2) / n - sample**2)
    gamma_hat = np.sum((sample - target) ** 2)
    shrinkage = max(0.0, min(1.0, pi_hat / (gamma_hat * n)))
    return shrinkage * target + (1 - shrinkage) * sample


def test_matches_reference_implementation():
    """cov1para reproduces an independent reference computation to float tolerance."""
    rng = np.random.default_rng(0)
    Y = rng.standard_normal((200, 4))
    np.testing.assert_allclose(cov1para(Y), _reference_cov1para(Y))


def test_scaled_identity_input_is_a_fixed_point():
    """When the sample covariance already is a scaled identity, so is the result.

    Sample and target coincide, so the result equals that scaled identity for any
    shrinkage weight: equal diagonal entries and zero off-diagonal entries. This
    pins the scaled-identity target structure independently of the weight.
    """
    # Two orthogonal, equal-norm columns -> Y.T @ Y is a scaled identity.
    Y = np.array([[1.0, 1.0], [1.0, -1.0], [-1.0, 1.0], [-1.0, -1.0]])
    # sample == target gives gamma_hat == 0; the clamp still yields the target.
    with np.errstate(divide="ignore"):
        result = cov1para(Y, k=0)
    diag = np.diag(result)
    off_diagonal = result - np.diag(diag)
    np.testing.assert_allclose(off_diagonal, np.zeros((2, 2)), atol=1e-12)
    np.testing.assert_allclose(diag, np.full(2, diag[0]))


def test_shrinkage_within_unit_interval(rng):
    """The estimator stays between the sample covariance and the target.

    A convex combination with weight in [0, 1] keeps every entry bounded by the
    corresponding sample and target entries, which fails if the weight escapes
    the clamp.
    """
    Y = rng.standard_normal((40, 4))
    n = Y.shape[0] - 1
    Yd = Y - Y.mean(axis=0)
    sample = (Yd.T @ Yd) / n
    target = np.diag(sample).mean() * np.eye(4)
    result = cov1para(Y)
    lo = np.minimum(sample, target)
    hi = np.maximum(sample, target)
    assert np.all(result >= lo - 1e-10)
    assert np.all(result <= hi + 1e-10)


def test_single_variable_returns_sample_variance(rng):
    """For p=1 the target equals the sample, so the result is the sample variance."""
    Y = rng.standard_normal((100, 1))
    n = Y.shape[0] - 1
    Yd = Y - Y.mean(axis=0)
    expected = (Yd.T @ Yd) / n
    # p == 1 makes sample == target (gamma_hat == 0); the clamp pins shrinkage.
    with np.errstate(divide="ignore"):
        result = cov1para(Y)
    np.testing.assert_allclose(result, expected)
