import pytest
from sample_data import (
    BATS,
    GLOVES,
    HELMETS,
    LUCAS_TICKET,
    MAYA_TICKET,
    load_locker,
)

from equipment.locker import (
    ConflictError,
    LockerApp,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from equipment.types import EquipmentView, TicketSummary


@pytest.fixture
def app(store):
    return LockerApp(store)


def test_health_ok(app):
    app.health()


def test_health_raises_when_database_unreachable(down_store):
    locker = LockerApp(down_store)
    with pytest.raises(ServiceUnavailableError):
        locker.health()


def test_add_equipment_strips_name_and_stores_total(app, store):
    created = app.add_equipment("  Softball gloves  ", 12)
    assert len(created.equipment_id) == 8
    assert created.item_name == "Softball gloves"
    assert created.total == 12
    assert created.available == 12

    stored = store.get_equipment(created.equipment_id)
    assert stored is not None
    assert stored.item_name == "Softball gloves"
    assert stored.total == 12


@pytest.mark.parametrize(
    "item_name, total",
    [
        ("", 12),
        ("   ", 12),
        ("x" * 65, 12),
        ("Softball gloves", -1),
        ("Softball gloves", True),
        ("Softball gloves", "12"),
    ],
)
def test_add_equipment_validation(app, item_name, total):
    with pytest.raises(ValidationError):
        app.add_equipment(item_name, total)


def test_list_equipment_empty(app):
    assert app.list_equipment() == []


def test_list_equipment_shows_available_and_sorts_by_name(app, store):
    load_locker(store)
    assert app.list_equipment() == [
        EquipmentView("b9q4vs1b", "Baseballs", 24, 21),
        EquipmentView("a8w3mn4f", "Bases", 4, 4),
        EquipmentView("k7m1xq9p", "Bats", 2, 0),
        EquipmentView("c2t7yh5d", "Catcher's gear", 3, 3),
        EquipmentView("g4n8kp2w", "Gloves", 12, 12),
        EquipmentView("h2p6rt3c", "Helmets", 10, 9),
    ]


def test_list_tickets_for_bats_is_lucas_only(app, store):
    load_locker(store)
    assert app.list_tickets(BATS.equipment_id) == [
        TicketSummary(ticket_id=LUCAS_TICKET.ticket_id, name="Lucas", quantity=2)
    ]


def test_list_tickets_newest_first(app, store):
    load_locker(store)
    created = app.create_ticket("Sam", 1, HELMETS.equipment_id)
    summaries = app.list_tickets(HELMETS.equipment_id)
    assert summaries == [
        TicketSummary(ticket_id=created.ticket_id, name="Sam", quantity=1),
        TicketSummary(ticket_id=MAYA_TICKET.ticket_id, name="Maya", quantity=1),
    ]


def test_list_tickets_not_found(app):
    with pytest.raises(NotFoundError):
        app.list_tickets("does-not-exist")


def test_create_ticket_borrows_gloves(app, store):
    load_locker(store)
    ticket = app.create_ticket("  Alex  ", 1, GLOVES.equipment_id)
    assert len(ticket.ticket_id) == 8
    assert ticket.name == "Alex"
    assert ticket.quantity == 1
    assert ticket.equipment_id == GLOVES.equipment_id
    assert ticket.created_at.endswith("Z")

    gloves = next(item for item in app.list_equipment() if item.item_name == "Gloves")
    assert gloves.total == 12
    assert gloves.available == 11
    assert app.list_tickets(GLOVES.equipment_id) == [
        TicketSummary(ticket_id=ticket.ticket_id, name="Alex", quantity=1)
    ]


def test_create_ticket_rejects_more_than_available(app, store):
    load_locker(store)
    with pytest.raises(ConflictError):
        app.create_ticket("Alex", 1, BATS.equipment_id)
    assert store.list_tickets(BATS.equipment_id) == [LUCAS_TICKET]


@pytest.mark.parametrize(
    "name, quantity",
    [
        ("", 1),
        ("   ", 1),
        ("x" * 65, 1),
        ("Alex", 0),
        ("Alex", -1),
        ("Alex", True),
    ],
)
def test_create_ticket_validation(app, store, name, quantity):
    load_locker(store)
    with pytest.raises(ValidationError):
        app.create_ticket(name, quantity, GLOVES.equipment_id)


def test_create_ticket_equipment_not_found(app):
    with pytest.raises(NotFoundError):
        app.create_ticket("Alex", 1, "does-not-exist")


def test_get_ticket(app, store):
    load_locker(store)
    assert app.get_ticket(LUCAS_TICKET.ticket_id) == LUCAS_TICKET


def test_get_ticket_not_found(app):
    with pytest.raises(NotFoundError):
        app.get_ticket("does-not-exist")


def test_return_ticket_restores_bats(app, store):
    load_locker(store)
    app.return_ticket(LUCAS_TICKET.ticket_id)

    with pytest.raises(NotFoundError):
        app.get_ticket(LUCAS_TICKET.ticket_id)
    assert app.list_tickets(BATS.equipment_id) == []

    bats = next(item for item in app.list_equipment() if item.item_name == "Bats")
    assert bats.total == 2
    assert bats.available == 2


def test_return_ticket_not_found(app):
    with pytest.raises(NotFoundError):
        app.return_ticket("does-not-exist")
