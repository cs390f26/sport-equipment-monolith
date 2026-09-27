import sys

from flask import Flask, jsonify, request

from equipment.db import DatabaseUnavailableError, EquipmentStorage
from equipment.locker import (
    ConflictError,
    LockerApp,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from equipment.settings import ensure_settings
from equipment.types import EquipmentView, TicketData, TicketSummary


def _error(message: str, status: int):
    return jsonify({"message": message}), status


def _equipment_json(item: EquipmentView) -> dict:
    return {
        "equipmentId": item.equipment_id,
        "itemName": item.item_name,
        "total": item.total,
        "available": item.available,
    }


def _summary_json(ticket: TicketSummary) -> dict:
    return {
        "ticketId": ticket.ticket_id,
        "name": ticket.name,
        "quantity": ticket.quantity,
    }


def _ticket_json(ticket: TicketData) -> dict:
    return {
        "ticketId": ticket.ticket_id,
        "createdAt": ticket.created_at,
        "name": ticket.name,
        "quantity": ticket.quantity,
        "equipmentId": ticket.equipment_id,
    }


def create_app(locker_app: LockerApp) -> Flask:
    """Build the Flask app and add routes."""
    app = Flask(__name__)

    @app.get("/health")
    def health():
        try:
            locker_app.health()
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        return jsonify({"status": "ok"}), 200

    @app.get("/equipment")
    def list_equipment():
        try:
            items = locker_app.list_equipment()
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        return jsonify([_equipment_json(item) for item in items]), 200

    @app.post("/equipment")
    def add_equipment():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _error("JSON body required", 400)
        if "itemName" not in body or "total" not in body:
            return _error("itemName and total are required", 400)
        try:
            created = locker_app.add_equipment(body["itemName"], body["total"])
        except ValidationError as exc:
            return _error(str(exc), 400)
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        response = jsonify(_equipment_json(created))
        response.status_code = 201
        response.headers["Location"] = f"/equipment/{created.equipment_id}"
        return response

    @app.get("/tickets")
    def list_tickets():
        equipment_id = request.args.get("equipmentId")
        if not equipment_id:
            return _error("equipmentId query parameter is required", 400)
        try:
            tickets = locker_app.list_tickets(equipment_id)
        except NotFoundError:
            return _error("Equipment not found", 404)
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        return jsonify([_summary_json(ticket) for ticket in tickets]), 200

    @app.post("/tickets")
    def create_ticket():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _error("JSON body required", 400)
        if "name" not in body or "quantity" not in body or "equipmentId" not in body:
            return _error("name, quantity, and equipmentId are required", 400)
        try:
            ticket = locker_app.create_ticket(
                body["name"],
                body["quantity"],
                body["equipmentId"],
            )
        except ValidationError as exc:
            return _error(str(exc), 400)
        except ConflictError as exc:
            return _error(str(exc), 409)
        except NotFoundError:
            return _error("Equipment not found", 404)
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        response = jsonify(_ticket_json(ticket))
        response.status_code = 201
        response.headers["Location"] = f"/tickets/{ticket.ticket_id}"
        return response

    @app.get("/tickets/<ticket_id>")
    def get_ticket(ticket_id):
        try:
            ticket = locker_app.get_ticket(ticket_id)
        except NotFoundError:
            return _error("Ticket not found", 404)
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        return jsonify(_ticket_json(ticket)), 200

    @app.delete("/tickets/<ticket_id>")
    def return_ticket(ticket_id):
        try:
            locker_app.return_ticket(ticket_id)
        except NotFoundError:
            return _error("Ticket not found", 404)
        except ServiceUnavailableError:
            return jsonify({"status": "unavailable"}), 503
        return "", 204

    return app


def launch() -> Flask:
    """Build EquipmentStorage + LockerApp + Flask app from settings."""
    settings = ensure_settings()
    storage = EquipmentStorage.from_settings(settings)
    try:
        storage.ping()
    except DatabaseUnavailableError as exc:
        raise RuntimeError(
            "Database not reachable. Is Aurora running? "
            "Are the Equipment and Ticket tables created "
            "(python scripts/create_table.py)? "
            f"Details: {exc}"
        ) from exc
    return create_app(LockerApp(storage))


if __name__ == "__main__":
    try:
        app = launch()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    app.run(debug=True, port=5000)
