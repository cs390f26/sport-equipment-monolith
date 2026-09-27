import pytest
from sample_data import (
    BATS,
    CATCHERS_GEAR,
    GLOVES,
    LOCKER_EQUIPMENT,
    LOCKER_TICKETS,
    LUCAS_TICKET,
    MAYA_TICKET,
    load_locker,
)

from equipment.db import (
    DatabaseUnavailableError,
    EquipmentAlreadyExistsError,
    EquipmentNotFoundError,
    EquipmentStorage,
    TicketAlreadyExistsError,
    TicketNotFoundError,
)


def test_init_requires_host():
    with pytest.raises(ValueError, match="host"):
        EquipmentStorage(host="", port=3306, user="root", password="", database="equipment")


def test_init_requires_user():
    with pytest.raises(ValueError, match="user"):
        EquipmentStorage(
            host="127.0.0.1",
            port=3306,
            user="",
            password="",
            database="equipment",
        )


def test_init_requires_database():
    with pytest.raises(ValueError, match="database"):
        EquipmentStorage(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="",
            database="",
        )


def test_ping_succeeds_when_tables_exist(store):
    store.ping()


def test_ping_raises_when_tables_missing(empty_store):
    with pytest.raises(DatabaseUnavailableError):
        empty_store.ping()


def test_ping_raises_when_server_unreachable(down_store):
    with pytest.raises(DatabaseUnavailableError):
        down_store.ping()


def test_add_and_get_equipment(store):
    store.add_equipment(BATS)
    assert store.get_equipment(BATS.equipment_id) == BATS


def test_get_equipment_returns_none_when_missing(store):
    assert store.get_equipment("does-not-exist") is None


def test_add_equipment_raises_when_id_exists(store):
    store.add_equipment(BATS)
    with pytest.raises(EquipmentAlreadyExistsError):
        store.add_equipment(BATS)


def test_add_equipment_keeps_apostrophe_in_name(store):
    store.add_equipment(CATCHERS_GEAR)
    assert store.get_equipment(CATCHERS_GEAR.equipment_id) == CATCHERS_GEAR


def test_list_equipment_empty(store):
    assert store.list_equipment() == []


def test_list_equipment_returns_all(store):
    load_locker(store)
    found = store.list_equipment()
    assert len(found) == len(LOCKER_EQUIPMENT)
    for equipment in LOCKER_EQUIPMENT:
        assert equipment in found


def test_clear_all_removes_equipment_and_tickets(store):
    load_locker(store)
    store.clear_all()
    assert store.list_equipment() == []
    assert store.list_tickets(BATS.equipment_id) == []


def test_add_and_get_ticket(store):
    store.add_equipment(BATS)
    store.add_ticket(LUCAS_TICKET)
    assert store.get_ticket(LUCAS_TICKET.ticket_id) == LUCAS_TICKET


def test_get_ticket_returns_none_when_missing(store):
    assert store.get_ticket("does-not-exist") is None


def test_add_ticket_raises_when_id_exists(store):
    store.add_equipment(BATS)
    store.add_ticket(LUCAS_TICKET)
    with pytest.raises(TicketAlreadyExistsError):
        store.add_ticket(LUCAS_TICKET)


def test_add_ticket_raises_when_equipment_missing(store):
    with pytest.raises(EquipmentNotFoundError):
        store.add_ticket(LUCAS_TICKET)


def test_list_tickets_for_one_item(store):
    load_locker(store)
    assert store.list_tickets(BATS.equipment_id) == [LUCAS_TICKET]
    assert store.list_tickets(GLOVES.equipment_id) == []


def test_list_tickets_returns_every_sample_ticket(store):
    load_locker(store)
    found = []
    for equipment in LOCKER_EQUIPMENT:
        found.extend(store.list_tickets(equipment.equipment_id))
    assert len(found) == len(LOCKER_TICKETS)
    for ticket in LOCKER_TICKETS:
        assert ticket in found
    assert MAYA_TICKET in found


def test_delete_ticket(store):
    store.add_equipment(BATS)
    store.add_ticket(LUCAS_TICKET)
    store.delete_ticket(LUCAS_TICKET.ticket_id)
    assert store.get_ticket(LUCAS_TICKET.ticket_id) is None
    assert store.get_equipment(BATS.equipment_id) == BATS


def test_delete_ticket_raises_when_missing(store):
    with pytest.raises(TicketNotFoundError):
        store.delete_ticket("does-not-exist")
