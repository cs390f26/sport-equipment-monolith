import pytest

from equipment.db import EquipmentStorage

# Fixtures here are available to every test module in this directory.
# Unit tests use an in-memory database, so pytest does not need MySQL.
# The running app still connects to MySQL through .env.


@pytest.fixture
def store():
    storage = EquipmentStorage.in_memory()
    storage.create_schema()
    yield storage
    storage.close()


@pytest.fixture
def empty_store():
    """In-memory database with no Equipment or Ticket tables."""
    storage = EquipmentStorage.in_memory()
    yield storage
    storage.close()


@pytest.fixture
def down_store():
    """Storage pointed at a closed port, so MySQL cannot be reached."""
    return EquipmentStorage(
        host="127.0.0.1",
        port=1,
        user="root",
        password="",
        database="equipment",
    )
