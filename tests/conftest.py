"""Fixtures for tests.
"""

from pathlib import Path

import polars as pl
import pytest


@pytest.fixture(scope="session")
def resource_dir():
    """Fixture that provides the path to the test resources directory."""
    return Path(__file__).parent / "resources"
