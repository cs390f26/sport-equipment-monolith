import secrets
from datetime import UTC, datetime

from equipment.db import (
    DatabaseUnavailableError,
    EquipmentAlreadyExistsError,
    EquipmentNotFoundError,
    EquipmentStorage,
    TicketAlreadyExistsError,
    TicketNotFoundError,
)
from equipment.types import (
    EquipmentData,
    EquipmentView,
    TicketData,
    TicketSummary,
    equipment_view,
    ticket_summary,
)


class ValidationError(Exception):
    """Raised when input fails application rules."""


class NotFoundError(Exception):
    """Raised when an equipment id or ticket id does not exist."""


class ConflictError(Exception):
    """Raised when a borrow asks for more than the available quantity."""


class ServiceUnavailableError(Exception):
    """Raised when the data store cannot be reached."""


class LockerApp:
    """Application rules for the equipment locker. Construct with EquipmentStorage."""

    def __init__(self, storage: EquipmentStorage):
        self._store = storage

    def health(self) -> None:
        """Check that the store is reachable.

        Raises ServiceUnavailableError if the database is not usable.
        """
        try:
            self._store.ping()
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc

    def list_equipment(self) -> list[EquipmentView]:
        """Return every item, ordered by name, with available quantity filled in."""
        try:
            rows = self._store.list_equipment()
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc

        views = []
        for equipment in rows:
            borrowed = self._borrowed(equipment.equipment_id)
            views.append(equipment_view(equipment, borrowed))
        views.sort(key=lambda item: item.item_name.casefold())
        return views

    def add_equipment(self, item_name: str, total: int) -> EquipmentView:
        """Validate input, store a new item, and return it with nothing borrowed."""
        if not isinstance(item_name, str):
            raise ValidationError("The item name must be a string.")
        if isinstance(total, bool) or not isinstance(total, int):
            raise ValidationError("The total quantity must be an integer.")

        item_name = item_name.strip()
        if not item_name:
            raise ValidationError("The item name must not be blank.")
        if len(item_name) > 64:
            raise ValidationError("The item name must be at most 64 characters.")
        if total < 0:
            raise ValidationError("The total quantity must be at least 0.")

        equipment = EquipmentData(
            equipment_id=secrets.token_hex(4),
            item_name=item_name,
            total=total,
        )
        try:
            self._store.add_equipment(equipment)
        except EquipmentAlreadyExistsError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because an equipment ID collision occurred."
            ) from exc
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc
        return equipment_view(equipment, 0)

    def list_tickets(self, equipment_id: str) -> list[TicketSummary]:
        """Return open tickets for one item, newest first.

        Raises NotFoundError if the equipment id does not exist.
        """
        self._require_equipment(equipment_id)
        try:
            tickets = self._store.list_tickets(equipment_id)
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc
        tickets.sort(key=lambda ticket: ticket.created_at, reverse=True)
        return [ticket_summary(ticket) for ticket in tickets]

    def create_ticket(self, name: str, quantity: int, equipment_id: str) -> TicketData:
        """Borrow one item if the quantity is at least 1 and not above available."""
        if not isinstance(name, str):
            raise ValidationError("The name must be a string.")
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValidationError("The quantity must be an integer.")
        if not isinstance(equipment_id, str) or not equipment_id.strip():
            raise ValidationError("The equipment ID must not be blank.")

        name = name.strip()
        if not name:
            raise ValidationError("The name must not be blank.")
        if len(name) > 64:
            raise ValidationError("The name must be at most 64 characters.")
        if quantity < 1:
            raise ValidationError("The quantity must be at least 1.")

        equipment = self._require_equipment(equipment_id)
        available = equipment.total - self._borrowed(equipment_id)
        if quantity > available:
            raise ConflictError(
                "Not enough equipment is available for that request. "
                "Please choose a smaller quantity."
            )

        ticket = TicketData(
            ticket_id=secrets.token_hex(4),
            created_at=_now_utc(),
            name=name,
            quantity=quantity,
            equipment_id=equipment_id,
        )
        try:
            self._store.add_ticket(ticket)
        except EquipmentNotFoundError as exc:
            raise NotFoundError(f"Equipment {equipment_id!r} was not found.") from exc
        except TicketAlreadyExistsError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because a ticket ID collision occurred."
            ) from exc
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc
        return ticket

    def get_ticket(self, ticket_id: str) -> TicketData:
        """Return one open ticket, or raise NotFoundError."""
        try:
            ticket = self._store.get_ticket(ticket_id)
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc
        if ticket is None:
            raise NotFoundError(f"Ticket {ticket_id!r} was not found.")
        return ticket

    def return_ticket(self, ticket_id: str) -> None:
        """Delete an open ticket so its quantity becomes available again."""
        self.get_ticket(ticket_id)
        try:
            self._store.delete_ticket(ticket_id)
        except TicketNotFoundError as exc:
            raise NotFoundError(f"Ticket {ticket_id!r} was not found.") from exc
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc

    def _require_equipment(self, equipment_id: str) -> EquipmentData:
        try:
            equipment = self._store.get_equipment(equipment_id)
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc
        if equipment is None:
            raise NotFoundError(f"Equipment {equipment_id!r} was not found.")
        return equipment

    def _borrowed(self, equipment_id: str) -> int:
        try:
            tickets = self._store.list_tickets(equipment_id)
        except DatabaseUnavailableError as exc:
            raise ServiceUnavailableError(
                "The service is unavailable because the database cannot be reached."
            ) from exc
        return sum(ticket.quantity for ticket in tickets)


def _now_utc() -> str:
    now = datetime.now(UTC)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
