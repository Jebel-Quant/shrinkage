"""The quadratic-inverse shrinkage (QIS) nonlinear estimator of Ledoit and Wolf."""

from __future__ import annotations

import numpy as np

from shrinkage._validation import effective_sample_size, validate_observation_matrix


def nonlinear_shrinkage(Y: np.ndarray, k: int | float | None = None) -> np.ndarray:
    """Quadratic-inverse shrinkage (QIS) of the sample covariance matrix.

    Estimates the covariance matrix by shrinking each *sample eigenvalue*
    individually toward the value that minimises the expected loss, using the
    closed-form quadratic-inverse shrinkage estimator of Ledoit and Wolf. QIS is
    derived under the Frobenius loss (and its inverse-Stein and minimum-variance
    cousins) and, unlike :func:`shrinkage.linear.cov1para` — which applies a
    single scalar intensity toward a scaled-identity target — reshapes the whole
    eigenvalue spectrum while keeping the sample eigenvectors. It is well defined
    both when p <= n and when the sample covariance is singular (p > n).

    Parameters
    ----------
    Y:
        Raw data matrix of shape (N, p): N iid observations on p variables. The
        estimator targets the large-dimensional regime where p is comparable to
        (or larger than) N.
    k:
        Demeaning control. None (default) or a float NaN: demean Y, reduce the
        effective sample size by 1. 0: no demeaning. 1: Y is already demeaned.

    Returns:
    -------
    Symmetric positive semi-definite covariance estimator of shape (p, p) whose
    trace matches the sample covariance's trace.

    Raises:
    ------
    ValueError
        If ``Y`` is not a 2-D array, has no variables or observations, contains
        non-finite values, or the effective sample size ``n = N - k`` is not
        positive. The message names the offending argument/condition.

    Notes:
    -----
    Port of the reference ``QIS`` implementation from Ledoit and Wolf's
    covariance-shrinkage code (https://github.com/pald22/covShrinkage), using
    :func:`numpy.linalg.eigh` for the symmetric spectral decomposition.

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(42)
        >>> Y = rng.standard_normal((100, 30))
        >>> nonlinear_shrinkage(Y).shape
        (30, 30)
    """
    N, p = validate_observation_matrix(Y)

    if k is None or (isinstance(k, float) and np.isnan(k)):
        Y = Y - Y.mean(axis=0)
        k = 1

    n = effective_sample_size(N, k)
    c = p / n  # concentration ratio

    sample = (Y.T @ Y) / n
    sample = (sample + sample.T) / 2.0  # enforce exact symmetry

    # eigh returns eigenvalues in ascending order with orthonormal eigenvectors.
    lam, u = np.linalg.eigh(sample)
    lam = lam.clip(min=0.0)  # reset tiny negative rounding artefacts to zero

    # Inverse of the min(p, n) non-null (largest) eigenvalues.
    pn = min(p, int(n))
    invlambda = 1.0 / lam[p - pn :]

    # Smoothed Stein shrinker and its Hilbert-transform conjugate.
    h = (min(c**2, 1.0 / c**2) ** 0.35) / p**0.35  # smoothing parameter
    Lj = np.tile(invlambda.reshape(-1, 1), (1, pn))
    Lj_i = Lj - Lj.T
    denom = Lj_i**2 + Lj**2 * h**2
    theta = np.mean(Lj * Lj_i / denom, axis=0)
    htheta = np.mean(Lj * Lj * h / denom, axis=0)
    atheta2 = theta**2 + htheta**2

    if p <= n:
        # Non-singular sample covariance: optimally shrunk eigenvalues.
        denom = (1.0 - c) ** 2 * invlambda + 2.0 * c * (1.0 - c) * invlambda * theta + c**2 * invlambda * atheta2
        delta = 1.0 / denom
    else:
        # Singular sample covariance: shrink the p - n null eigenvalues too.
        delta0 = 1.0 / ((c - 1.0) * np.mean(invlambda))
        delta = np.concatenate([np.repeat(delta0, p - pn), 1.0 / (invlambda * atheta2)])

    delta_qis = delta * (lam.sum() / delta.sum())  # preserve the trace
    estimator: np.ndarray = u @ (delta_qis[:, None] * u.T)
    return estimator
