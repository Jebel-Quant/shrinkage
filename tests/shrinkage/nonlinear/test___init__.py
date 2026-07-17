"""Tests for the shrinkage.nonlinear package API surface.

The estimator implementation and its numerical tests live in
:mod:`tests.shrinkage.nonlinear.test_qis`; this module only pins the thin
re-export contract of the package initializer.
"""

import shrinkage.nonlinear
from shrinkage.nonlinear import nonlinear_shrinkage
from shrinkage.nonlinear.qis import nonlinear_shrinkage as nonlinear_shrinkage_impl


def test_nonlinear_shrinkage_re_exported_from_dedicated_module():
    """The package re-exports the estimator defined in the qis module."""
    assert nonlinear_shrinkage is nonlinear_shrinkage_impl


def test_nonlinear_shrinkage_in_dunder_all():
    """nonlinear_shrinkage is listed in the subpackage __all__."""
    assert shrinkage.nonlinear.__all__ == ["nonlinear_shrinkage"]
