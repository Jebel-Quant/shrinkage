"""Shared input validation for shrinkage estimators.

The estimators in :mod:`shrinkage.linear` and :mod:`shrinkage.nonlinear` accept
the same raw ``(N, p)`` observation matrix, so they share the same up-front
checks. Centralising them here keeps the error messages consistent and means the
degenerate-input contract is defined in exactly one place.
"""

from __future__ import annotations

import numpy as np


def validate_observation_matrix(Y: np.ndarray) -> tuple[int, int]:
    """Validate a raw ``(N, p)`` observation matrix and return its shape.

    Parameters
    ----------
    Y:
        Raw data matrix expected to have shape ``(N, p)``: ``N`` observations on
        ``p`` variables.

    Returns:
    -------
    The ``(N, p)`` shape of ``Y`` once it has passed validation.

    Raises:
    ------
    ValueError
        If ``Y`` is not two-dimensional, has no variables (``p == 0``), has no
        observations (``N == 0``), or contains non-finite values (NaN/Inf). Each
        message names the offending condition and the received shape.
    """
    if Y.ndim != 2:
        raise ValueError(f"Y must be a 2-D (N, p) array; got a {Y.ndim}-D array of shape {Y.shape}.")
    N, p = Y.shape
    if p < 1:
        raise ValueError(f"Y must have at least one variable (column); got shape {Y.shape}.")
    if N < 1:
        raise ValueError(f"Y must have at least one observation (row); got shape {Y.shape}.")
    if not np.all(np.isfinite(Y)):
        raise ValueError("Y must contain only finite values; found NaN or infinity.")
    return N, p


def effective_sample_size(N: int, k: int | float) -> int | float:
    """Return the effective sample size ``n = N - k`` after demeaning control.

    Parameters
    ----------
    N:
        Number of observations (rows of the data matrix).
    k:
        Demeaning control already resolved to a number (``1`` when the data was
        demeaned in-estimator, ``0`` when it was not).

    Returns:
    -------
    The effective sample size ``n = N - k``.

    Raises:
    ------
    ValueError
        If ``n = N - k`` is not strictly positive, which would otherwise surface
        as a low-level ``ZeroDivisionError``/``FloatingPointError`` deep inside
        the covariance computation.
    """
    n = N - k
    if n <= 0:
        raise ValueError(
            f"Effective sample size n = N - k must be positive; got N={N}, k={k} giving n={n}. "
            "Provide more observations or a smaller demeaning control k."
        )
    return n
