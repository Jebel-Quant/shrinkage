"""Fixtures for tests.

Security exceptions in tests (S101 assert, S603/S607 subprocess) are safe here
because tests run in isolated environments and never reach production.
"""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def resource_dir():
    """Fixture that provides the path to the test resources directory."""
    return Path(__file__).parent / "resources"
