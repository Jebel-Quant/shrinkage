"""Tests for the top-level shrinkage package API surface."""

import shrinkage


def test_cov1para_importable_from_package_root():
    """cov1para is re-exported from the package root."""
    from shrinkage import cov1para

    assert cov1para is shrinkage.linear.cov1para


def test_cov1para_in_dunder_all():
    """cov1para is listed in the package __all__."""
    assert "cov1para" in shrinkage.__all__
