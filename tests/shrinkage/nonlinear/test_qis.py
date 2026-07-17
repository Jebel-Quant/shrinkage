"""Tests for the quadratic-inverse shrinkage (QIS) nonlinear estimator."""

import numpy as np
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from hypothesis.extra import numpy as hnp

from shrinkage.nonlinear import nonlinear_shrinkage


@pytest.fixture
def rng():
    """Provide a seeded NumPy random generator for reproducible tests."""
    return np.random.default_rng(42)


def _reference_qis(Y: np.ndarray, k: int | None = None) -> np.ndarray:
    """Independent transcription of the reference QIS estimator.

    Ports the published ``QIS`` routine from Ledoit and Wolf's covariance
    shrinkage code (https://github.com/pald22/covShrinkage) directly, so the
    test pins the production implementation to the numerical reference rather
    than only to structural invariants.
    """
    N, p = Y.shape
    if k is None or (isinstance(k, float) and np.isnan(k)):
        Y = Y - Y.mean(axis=0)
        k = 1
    n = N - k
    c = p / n
    sample = (Y.T @ Y) / n
    sample = (sample + sample.T) / 2
    lam, u = np.linalg.eigh(sample)
    lam = lam.clip(min=0)
    h = (min(c**2, 1 / c**2) ** 0.35) / p**0.35
    invlambda = 1 / lam[max(1, p - n + 1) - 1 : p]
    m = min(p, n)
    Lj = np.tile(invlambda.reshape(-1, 1), (1, m))
    Lj_i = Lj - Lj.T
    theta = np.mean(Lj * Lj_i / (Lj_i**2 + Lj**2 * h**2), axis=0)
    htheta = np.mean(Lj * Lj * h / (Lj_i**2 + Lj**2 * h**2), axis=0)
    atheta2 = theta**2 + htheta**2
    if p <= n:
        delta = 1 / ((1 - c) ** 2 * invlambda + 2 * c * (1 - c) * invlambda * theta + c**2 * invlambda * atheta2)
    else:
        delta0 = 1 / ((c - 1) * np.mean(invlambda))
        delta = np.concatenate([np.repeat(delta0, p - n), 1 / (invlambda * atheta2)])
    delta_qis = delta * (lam.sum() / delta.sum())
    return u @ np.diag(delta_qis) @ u.T


@pytest.mark.parametrize(("N", "p"), [(100, 30), (60, 5), (15, 40), (40, 40)])
def test_matches_reference_implementation(N, p):
    """QIS reproduces the reference computation across the p<n, p>n and p==n regimes."""
    Y = np.random.default_rng(N * p).standard_normal((N, p))
    np.testing.assert_allclose(nonlinear_shrinkage(Y), _reference_qis(Y), atol=1e-12)


def test_output_shape(rng):
    """The estimator returns a (p, p) matrix for p-variable input."""
    Y = rng.standard_normal((80, 12))
    assert nonlinear_shrinkage(Y).shape == (12, 12)


def test_symmetry(rng):
    """The shrinkage estimator is symmetric."""
    Y = rng.standard_normal((80, 12))
    result = nonlinear_shrinkage(Y)
    np.testing.assert_allclose(result, result.T, atol=1e-12)


@pytest.mark.parametrize(("N", "p"), [(80, 12), (12, 30)])
def test_positive_semidefinite(N, p):
    """The estimator is positive semi-definite in both the p<n and p>n regimes."""
    Y = np.random.default_rng(N).standard_normal((N, p))
    eigenvalues = np.linalg.eigvalsh(nonlinear_shrinkage(Y))
    assert np.all(eigenvalues >= -1e-10)


def test_trace_is_preserved(rng):
    """QIS rescales the shrunk eigenvalues to preserve the sample-covariance trace."""
    Y = rng.standard_normal((80, 20))
    Yd = Y - Y.mean(axis=0)
    sample = (Yd.T @ Yd) / (Y.shape[0] - 1)
    np.testing.assert_allclose(np.trace(nonlinear_shrinkage(Y)), np.trace(sample))


def test_k_none_demeans(rng):
    """k=None demeans the data, matching pre-demeaned input with k=1."""
    Y = rng.standard_normal((50, 6))
    np.testing.assert_allclose(nonlinear_shrinkage(Y), nonlinear_shrinkage(Y - Y.mean(axis=0), k=1))


def test_k0_no_demeaning(rng):
    """k=0 skips demeaning, so the result differs from the demeaned default."""
    Y = rng.standard_normal((50, 6)) + 5.0
    assert not np.allclose(nonlinear_shrinkage(Y, k=0), nonlinear_shrinkage(Y))


def test_k_nan_treated_as_none(rng):
    """A NaN value for k is treated identically to k=None."""
    Y = rng.standard_normal((50, 6))
    np.testing.assert_allclose(nonlinear_shrinkage(Y, k=float("nan")), nonlinear_shrinkage(Y, k=None))


def test_low_dimensional_tracks_sample_covariance():
    """For p << N the estimator is close to the (reliable) sample covariance."""
    rng = np.random.default_rng(0)
    p, N = 5, 20000
    Y = rng.standard_normal((N, p))
    Yd = Y - Y.mean(axis=0)
    sample = (Yd.T @ Yd) / (N - 1)
    result = nonlinear_shrinkage(Y)
    assert np.linalg.norm(result - sample) / np.linalg.norm(sample) < 0.05


def test_high_dimensional_beats_sample_covariance():
    """For p > N, QIS is closer to the truth than the singular sample covariance."""
    rng = np.random.default_rng(1)
    p, N = 80, 50
    A = rng.standard_normal((p, p))
    true = A @ A.T
    chol = np.linalg.cholesky(true)
    qis_loss, sample_loss = [], []
    for _ in range(10):
        Y = (chol @ rng.standard_normal((p, N))).T
        qis_loss.append(np.linalg.norm(nonlinear_shrinkage(Y) - true))
        sample_loss.append(np.linalg.norm(np.cov(Y, rowvar=False) - true))
    assert np.mean(qis_loss) < np.mean(sample_loss)


@pytest.mark.parametrize(
    ("Y", "kwargs", "match"),
    [
        (np.zeros(3), {}, "2-D"),
        (np.zeros((5, 0)), {}, "at least one variable"),
        (np.zeros((0, 3)), {}, "at least one observation"),
        (np.array([[np.nan, 1.0], [2.0, 3.0]]), {}, "finite"),
        (np.zeros((1, 3)), {"k": 1}, "Effective sample size"),
    ],
)
def test_degenerate_inputs_raise_valueerror(Y, kwargs, match):
    """Degenerate inputs raise ValueError naming the offending condition."""
    with pytest.raises(ValueError, match=match):
        nonlinear_shrinkage(Y, **kwargs)


# Random data matrices spanning both the p<=n and p>n regimes. k=1
# (already-demeaned mode) keeps the effective sample size n == N > 0.
_data_matrices = st.tuples(
    st.integers(min_value=4, max_value=12),
    st.integers(min_value=2, max_value=14),
).flatmap(
    lambda shape: hnp.arrays(
        dtype=np.float64,
        shape=shape,
        elements=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    )
)


@pytest.mark.property
@given(Y=_data_matrices)
@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.filter_too_much])
def test_property_invariants(Y):
    """Over random shapes the estimator is symmetric and positive semi-definite.

    These structural guarantees must hold for every admissible input, across
    both the non-singular (p<=n) and singular (p>n) regimes, not just the fixed
    shapes the example-based tests cover.
    """
    N, p = Y.shape
    # Skip rank-deficient draws whose retained eigenvalues collapse to ~0: their
    # inverses blow up and the 0/0 boundary carries no extra invariant coverage.
    sample = (Y.T @ Y) / N
    retained = np.linalg.eigvalsh(sample)[p - min(p, N) :]
    assume(retained.min() > 1e-6)

    result = nonlinear_shrinkage(Y, k=1)

    np.testing.assert_allclose(result, result.T, atol=1e-8)
    eigenvalues = np.linalg.eigvalsh(result)
    assert np.all(eigenvalues >= -1e-8)
