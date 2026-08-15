"""Tests for the cov1para linear shrinkage estimator."""

import warnings

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra import numpy as hnp

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
    # sample == target gives gamma_hat == 0, which the estimator resolves to
    # shrinkage 1 directly rather than through a division by zero.
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
    # p == 1 makes sample == target (gamma_hat == 0), pinning shrinkage to 1.
    result = cov1para(Y)
    np.testing.assert_allclose(result, expected)


@pytest.mark.parametrize(
    ("Y", "kwargs"),
    [
        # p == 1: the scaled-identity target is the sample covariance by definition.
        (np.random.default_rng(42).standard_normal((100, 1)), {}),
        # Orthogonal equal-norm columns: Y.T @ Y is already a scaled identity.
        (np.array([[1.0, 1.0], [1.0, -1.0], [-1.0, 1.0], [-1.0, -1.0]]), {"k": 0}),
    ],
)
def test_degenerate_target_emits_no_warning(Y, kwargs):
    """Inputs where sample == target return cleanly instead of warning.

    Both cases drive gamma_hat to exactly zero. Computing the intensity by
    division would still yield the right answer -- inf, clamped to 1 -- but leak
    a numpy divide-by-zero RuntimeWarning to the caller for a perfectly valid
    input. The result must also stay finite and equal the target.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        result = cov1para(Y, **kwargs)

    assert np.all(np.isfinite(result))
    # shrinkage == 1 means the estimator is exactly the scaled-identity target.
    diag = np.diag(result)
    np.testing.assert_allclose(result, np.diag(diag))
    np.testing.assert_allclose(diag, np.full(Y.shape[1], diag[0]))


@pytest.mark.parametrize(
    ("Y", "kwargs", "match"),
    [
        (np.zeros(3), {}, "2-D"),
        (np.zeros((2, 2, 2)), {}, "2-D"),
        (np.zeros((5, 0)), {}, "at least one variable"),
        (np.zeros((0, 3)), {}, "at least one observation"),
        (np.array([[np.nan, 1.0], [2.0, 3.0]]), {}, "finite"),
        (np.array([[1.0, np.inf], [2.0, 3.0]]), {}, "finite"),
        (np.zeros((1, 3)), {"k": 1}, "Effective sample size"),
        (np.zeros((1, 3)), {}, "Effective sample size"),
    ],
)
def test_degenerate_inputs_raise_valueerror(Y, kwargs, match):
    """Degenerate inputs raise ValueError naming the offending condition."""
    with pytest.raises(ValueError, match=match):
        cov1para(Y, **kwargs)


def _recovered_intensity(Y: np.ndarray, result: np.ndarray, k: int) -> float | None:
    """Read the shrinkage intensity back out of the returned estimator.

    The public ``cov1para`` returns only the (p, p) matrix, not the weight, but
    that matrix is by definition ``s * target + (1 - s) * sample``. So ``s`` can
    be recovered by *inverting the convex combination* -- projecting
    ``sample - result`` onto ``sample - target`` -- rather than by recomputing
    the Ledoit-Wolf weight.

    That distinction is the point. Only the sample covariance and the
    scaled-identity target appear here, both of which are definitional; none of
    the estimator's own machinery (``pi_hat``, ``gamma_hat``, the clamp) is
    mentioned. An error in that machinery therefore shows up as a violated
    invariant instead of being mirrored into the assertion, and so does a weight
    applied the wrong way round -- which a recomputation cannot see at all,
    because it never looks at ``result``.

    Returns None when the weight is not identifiable: if the sample covariance
    already is the target then every weight produces the same estimator, and
    nothing can be read back from it. Near that boundary the projection loses
    precision in proportion to how small ``sample - target`` is, so the guard is
    relative to the size of the sample covariance rather than an exact zero.

    ``k`` is the resolved demeaning control (an int), not the public argument's
    ``None``/NaN sentinel: the callers below pass 1 or 0 explicitly.
    """
    N, p = Y.shape
    n = N - k
    sample = (Y.T @ Y) / n
    target = np.diag(sample).mean() * np.eye(p)
    spread = sample - target

    spread_norm2 = float(np.einsum("ij,ij->", spread, spread))
    sample_norm2 = float(np.einsum("ij,ij->", sample, sample))
    if spread_norm2 <= 1e-16 * sample_norm2:
        return None

    return float(np.einsum("ij,ij->", sample - result, spread)) / spread_norm2


# Random data matrices over a range of shapes. Bounds keep every example small
# and fast; values are finite and modestly scaled so the sample covariance is
# well defined. k=1 (already-demeaned mode) keeps n == N > 0 for every shape.
_data_matrices = st.tuples(
    st.integers(min_value=3, max_value=12),
    st.integers(min_value=2, max_value=8),
).flatmap(
    lambda shape: hnp.arrays(
        dtype=np.float64,
        shape=shape,
        elements=st.floats(
            min_value=-10.0,
            max_value=10.0,
            allow_nan=False,
            allow_infinity=False,
        ),
    )
)


@pytest.mark.property
@given(Y=_data_matrices)
@settings(max_examples=200, deadline=None)
def test_property_invariants(Y):
    """Over random shapes the estimator is symmetric, PSD, and shrinkage ∈ [0, 1].

    These are the defining structural and numerical guarantees of the
    Ledoit-Wolf one-parameter estimator and must hold for every admissible
    input, not just the fixed shapes the example-based tests cover.
    """
    # Degenerate draws where the sample covariance is already a scaled identity
    # are included rather than filtered out: the estimator returns the target
    # there, so symmetry and positive semi-definiteness hold on that boundary
    # too and are worth asserting. Only the weight is unidentifiable there.
    result = cov1para(Y, k=1)

    # Symmetry: a covariance estimator must equal its own transpose.
    np.testing.assert_allclose(result, result.T, atol=1e-10)

    # Positive semi-definite: no eigenvalue dips meaningfully below zero.
    eigenvalues = np.linalg.eigvalsh(result)
    assert np.all(eigenvalues >= -1e-8)

    # The convex weight actually applied stays inside the unit interval. The
    # tolerance absorbs the rounding the projection inherits from `result`;
    # None means this draw sits on the unidentifiable boundary described above.
    intensity = _recovered_intensity(Y, result, k=1)
    if intensity is not None:
        assert -1e-6 <= intensity <= 1.0 + 1e-6


def test_ill_conditioned_shrinkage_approaches_one():
    """For p ≫ N (high-dimensional) the shrinkage intensity approaches 1.

    When variables vastly outnumber observations the sample covariance is rank
    deficient and unreliable, so the estimator should lean almost entirely on
    the well-conditioned scaled-identity target. With a true scaled-identity
    covariance and p/N = 200, the returned estimator sits more than 90% of the
    way from the sample covariance to the target, and stays symmetric.
    """
    rng = np.random.default_rng(0)
    N, p = 20, 4000
    Y = rng.standard_normal((N, p))

    # k=0: the data is mean-zero by construction, so no demeaning is needed.
    result = cov1para(Y, k=0)

    # Read the weight back out of the returned matrix, so this asserts where the
    # estimator actually landed rather than what the intensity formula computes.
    intensity = _recovered_intensity(Y, result, k=0)
    assert intensity is not None
    assert intensity > 0.9

    # The estimator stays symmetric even in this degenerate regime. (A full
    # eigendecomposition of the 4000x4000 result is skipped for speed; the
    # property test above already covers positive semi-definiteness.)
    np.testing.assert_allclose(result, result.T, atol=1e-10)
