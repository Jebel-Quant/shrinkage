"""Tests for the shrinkage.linear package API surface.

The estimator implementation and its numerical tests live in
:mod:`tests.shrinkage.linear.test_cov1para`; this module only pins the thin
re-export contract of the package initializer.
"""

import shrinkage.linear
from shrinkage.linear import cov1para
from shrinkage.linear.cov1para import cov1para as cov1para_impl


def test_cov1para_re_exported_from_dedicated_module():
    """The package re-exports the estimator defined in the cov1para module."""
    assert cov1para is cov1para_impl


def test_cov1para_in_dunder_all():
    """cov1para is listed in the subpackage __all__."""
    assert shrinkage.linear.__all__ == ["cov1para"]
