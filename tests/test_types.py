from sample_data import BATS, LUCAS_TICKET

from equipment.types import (
    EquipmentView,
    TicketSummary,
    equipment_from_mapping,
    equipment_view,
    ticket_from_mapping,
    ticket_summary,
)


def test_equipment_from_mapping_and_available_view():
    equipment = equipment_from_mapping(
        {"equipmentId": "k7m1xq9p", "itemName": "Bats", "total": 2}
    )
    assert equipment == BATS
    assert equipment_view(equipment, borrowed=2) == EquipmentView(
        equipment_id="k7m1xq9p",
        item_name="Bats",
        total=2,
        available=0,
    )


def test_ticket_from_mapping():
    ticket = ticket_from_mapping(
        {
            "ticketId": "k7m2xq9p",
            "createdAt": "2026-07-28T12:15:00.000Z",
            "name": "Lucas",
            "quantity": 2,
            "equipmentId": "k7m1xq9p",
        }
    )
    assert ticket == LUCAS_TICKET


def test_ticket_summary_keeps_borrower_and_quantity():
    assert ticket_summary(LUCAS_TICKET) == TicketSummary(
        ticket_id="k7m2xq9p",
        name="Lucas",
        quantity=2,
    )
