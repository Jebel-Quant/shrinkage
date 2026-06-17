"""Linear shrinkage estimators for covariance matrices."""

import numpy as np


def cov1para(Y: np.ndarray, k: int | None = None) -> np.ndarray:
    """Linear shrinkage toward a scaled identity (one-parameter target).

    Shrinks the sample covariance matrix toward a target where all variances
    are equal and all covariances are zero. Ledoit and Wolf (2003, JEF).

    Parameters
    ----------
    Y:
        Raw data matrix of shape (N, p): N iid observations on p variables.
    k:
        Demeaning control. None (default): demean Y, reduce effective sample
        size by 1. 0: no demeaning. 1: Y is already demeaned.

    Returns:
    -------
    Shrinkage covariance estimator of shape (p, p).

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(42)
        >>> Y = rng.standard_normal((100, 3))
        >>> cov1para(Y).shape
        (3, 3)
    """
    N, p = Y.shape

    if k is None or (isinstance(k, float) and np.isnan(k)):
        Y = Y - Y.mean(axis=0)
        k = 1

    n = N - k
    sample = (Y.T @ Y) / n
    target = np.diag(sample).mean() * np.eye(p)

    Y2 = Y**2
    sample2 = (Y2.T @ Y2) / n
    pi_hat = np.sum(sample2 - sample**2)
    gamma_hat = np.linalg.norm(sample - target, ord="fro") ** 2

    shrinkage = max(0.0, min(1.0, pi_hat / (gamma_hat * n)))
    estimator: np.ndarray = shrinkage * target + (1 - shrinkage) * sample
    return estimator
