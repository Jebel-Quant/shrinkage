"""Tests for the top-level shrinkage package API surface."""

import shrinkage


def test_cov1para_importable_from_package_root():
    """cov1para is re-exported from the package root."""
    from shrinkage import cov1para

    assert cov1para is shrinkage.linear.cov1para


def test_nonlinear_shrinkage_importable_from_package_root():
    """nonlinear_shrinkage is re-exported from the package root."""
    from shrinkage import nonlinear_shrinkage

    assert nonlinear_shrinkage is shrinkage.nonlinear.nonlinear_shrinkage


def test_public_api_in_dunder_all():
    """Both estimators are listed in the package __all__."""
    assert shrinkage.__all__ == ["cov1para", "nonlinear_shrinkage"]
