"""Shared setup for Playwright acceptance tests.

Assumes the Flask app is already running on port 5000 and .env points at
the same Aurora database the app opened. This file checks that the app is
healthy and resets that database between tests.
"""

import urllib.error
import urllib.request

import pytest
from sample_data import load_locker

from equipment.db import EquipmentStorage
from equipment.settings import ensure_settings

BASE_URL = "http://127.0.0.1:5000"


def pytest_sessionstart(session):
    """Fail fast if the running app is not healthy."""
    health_url = f"{BASE_URL}/health"
    try:
        with urllib.request.urlopen(health_url, timeout=1.0) as response:
            if response.status != 200:
                pytest.exit(
                    f"{health_url} returned {response.status} (expected 200). "
                    "Is the app running (python -m equipment.app)?",
                    returncode=1,
                )
    except (urllib.error.URLError, OSError) as exc:
        pytest.exit(
            f"App not reachable at {BASE_URL}. "
            "Set the AURORA_* values in .env, create the tables, and run "
            "python -m equipment.app.\n"
            f"Details: {exc}",
            returncode=1,
        )


@pytest.fixture(scope="session")
def base_url():
    """URL of the already-running Flask app (pytest-playwright uses this)."""
    return BASE_URL


@pytest.fixture
def locker_storage():
    """Empty EquipmentStorage connected with ensure_settings."""
    settings = ensure_settings()
    storage = EquipmentStorage.from_settings(settings)
    storage.clear_all()
    return storage


@pytest.fixture
def sample_locker(locker_storage):
    """Scenario 1: six equipment rows and the Lucas, Jordan, and Maya tickets."""
    load_locker(locker_storage)
    return locker_storage
