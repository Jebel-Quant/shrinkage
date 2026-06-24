"""Fuzz the linear covariance-shrinkage estimator against arbitrary data.

``cov1para`` shrinks a sample covariance matrix toward a scaled-identity target
given a raw data matrix of shape ``(N, p)``. It must never crash with an
unexpected exception on adversarial input — degenerate shapes (empty,
single-observation), non-finite values and pathological demeaning controls
should produce a result (possibly non-finite) or raise a documented error. This
harness exercises that contract with coverage-guided input.

Run locally:
    pip install atheris numpy
    python tests/fuzz/fuzz_cov1para.py -atheris_runs=20000

Run in ClusterFuzzLite: this file is built by .clusterfuzzlite/build.sh.
"""

from __future__ import annotations

import contextlib
import sys

import atheris

# Pre-import numpy OUTSIDE the instrumentation block so it loads uninstrumented;
# only the first-party package under test is instrumented.
import numpy as np

with atheris.instrument_imports():
    from shrinkage.linear import cov1para

_ALLOWED = (ValueError, ZeroDivisionError, np.linalg.LinAlgError, FloatingPointError)


def test_one_input(data: bytes) -> None:
    """Run a fuzzed (N, p) data matrix through cov1para with varied demeaning."""
    fdp = atheris.FuzzedDataProvider(data)
    n_obs = fdp.ConsumeIntInRange(0, 12)
    n_var = fdp.ConsumeIntInRange(0, 6)
    floats = [fdp.ConsumeFloat() for _ in range(n_obs * n_var)]
    y = np.array(floats, dtype=np.float64).reshape(n_obs, n_var)
    # Exercise all three demeaning modes: auto-demean, none, already-demeaned.
    k = (None, 0, 1)[fdp.ConsumeIntInRange(0, 2)]

    with contextlib.suppress(_ALLOWED):
        cov1para(y, k)


def main() -> None:
    """Run the Atheris fuzz loop."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
