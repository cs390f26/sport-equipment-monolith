from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class EquipmentData:
    """One equipment row as stored in the Equipment table."""

    equipment_id: str
    item_name: str
    total: int


@dataclass(frozen=True)
class TicketData:
    """One ticket row as stored in the Ticket table."""

    ticket_id: str
    created_at: str
    name: str
    quantity: int
    equipment_id: str


@dataclass(frozen=True)
class EquipmentView:
    """Equipment as shown in the locker list.

    available is total minus the quantities on open tickets. It is not stored.
    """

    equipment_id: str
    item_name: str
    total: int
    available: int


@dataclass(frozen=True)
class TicketSummary:
    """Open ticket as shown on an equipment item's ticket list."""

    ticket_id: str
    name: str
    quantity: int


def equipment_from_mapping(row: Mapping) -> EquipmentData:
    """Build EquipmentData from a table row or the same keys."""
    return EquipmentData(
        equipment_id=row["equipmentId"],
        item_name=row["itemName"],
        total=int(row["total"]),
    )


def ticket_from_mapping(row: Mapping) -> TicketData:
    """Build TicketData from a table row or the same keys."""
    return TicketData(
        ticket_id=row["ticketId"],
        created_at=row["createdAt"],
        name=row["name"],
        quantity=int(row["quantity"]),
        equipment_id=row["equipmentId"],
    )


def equipment_view(equipment: EquipmentData, borrowed: int) -> EquipmentView:
    """Project a stored equipment row to the list view."""
    return EquipmentView(
        equipment_id=equipment.equipment_id,
        item_name=equipment.item_name,
        total=equipment.total,
        available=equipment.total - borrowed,
    )


def ticket_summary(ticket: TicketData) -> TicketSummary:
    """Project a stored ticket to the open-ticket list view."""
    return TicketSummary(
        ticket_id=ticket.ticket_id,
        name=ticket.name,
        quantity=ticket.quantity,
    )
