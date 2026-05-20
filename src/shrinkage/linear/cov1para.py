import numpy as np

from cvx.linalg import norm


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

    Returns
    -------
    Shrinkage covariance estimator of shape (p, p).
    """
    N, p = Y.shape

    if k is None or (isinstance(k, float) and np.isnan(k)):
        Y = Y - Y.mean(axis=0)
        k = 1

    n = N - k
    target2 = np.var(Y, axis=0, ddof=1).mean() * np.eye(p)

    sample = (Y.T @ Y) / n
    target = np.diag(sample).mean() * np.eye(p)
    print(f"target: {target}")
    print(f"target2: {target2}")

    Y2 = Y ** 2
    sample2 = (Y2.T @ Y2) / n
    pi_hat = np.sum(sample2 - sample ** 2)
    print(f"pi_hat: {pi_hat}")
    gamma_hat = norm(sample - target, ord="fro") ** 2
    print(f"gamma_hat: {gamma_hat}")
    print(f"gamma_hat / pi_hat: {pi_hat / (gamma_hat * n)}")
    shrinkage = max(0.0, min(1.0, pi_hat / (gamma_hat * n)))
    print(f"shrinkage: {shrinkage}")
    return shrinkage * target + (1 - shrinkage) * sample


if __name__ == '__main__':
    np.random.seed(0)
    X = np.random.randn(10, 4)
    XX = cov1para(X)
