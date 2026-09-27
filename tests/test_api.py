import pytest
from sample_data import BATS, GLOVES, LUCAS_TICKET, load_locker

from equipment.app import create_app
from equipment.locker import LockerApp


@pytest.fixture
def client(store):
    flask_app = create_app(LockerApp(store))
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_unavailable(down_store):
    flask_app = create_app(LockerApp(down_store))
    response = flask_app.test_client().get("/health")
    assert response.status_code == 503
    assert response.get_json() == {"status": "unavailable"}


def test_list_equipment_empty(client):
    response = client.get("/equipment")
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_equipment(client, store):
    load_locker(store)
    response = client.get("/equipment")
    assert response.status_code == 200
    assert response.get_json() == [
        {
            "equipmentId": "b9q4vs1b",
            "itemName": "Baseballs",
            "total": 24,
            "available": 21,
        },
        {"equipmentId": "a8w3mn4f", "itemName": "Bases", "total": 4, "available": 4},
        {"equipmentId": "k7m1xq9p", "itemName": "Bats", "total": 2, "available": 0},
        {
            "equipmentId": "c2t7yh5d",
            "itemName": "Catcher's gear",
            "total": 3,
            "available": 3,
        },
        {"equipmentId": "g4n8kp2w", "itemName": "Gloves", "total": 12, "available": 12},
        {
            "equipmentId": "h2p6rt3c",
            "itemName": "Helmets",
            "total": 10,
            "available": 9,
        },
    ]


def test_add_equipment(client):
    response = client.post(
        "/equipment",
        json={"itemName": "Softball gloves", "total": 12},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert len(body["equipmentId"]) == 8
    assert body["itemName"] == "Softball gloves"
    assert body["total"] == 12
    assert body["available"] == 12
    assert response.headers["Location"] == f"/equipment/{body['equipmentId']}"


def test_add_equipment_bad_request(client):
    response = client.post("/equipment", json={"itemName": "   ", "total": 12})
    assert response.status_code == 400
    assert response.get_json() == {"message": "itemName must not be blank"}


def test_add_equipment_requires_json(client):
    response = client.post("/equipment", data="nope", content_type="text/plain")
    assert response.status_code == 400
    assert response.get_json()["message"] == "JSON body required"


def test_list_tickets_for_bats(client, store):
    load_locker(store)
    response = client.get(f"/tickets?equipmentId={BATS.equipment_id}")
    assert response.status_code == 200
    assert response.get_json() == [
        {"ticketId": LUCAS_TICKET.ticket_id, "name": "Lucas", "quantity": 2}
    ]


def test_list_tickets_requires_equipment_id(client):
    response = client.get("/tickets")
    assert response.status_code == 400
    assert response.get_json() == {
        "message": "equipmentId query parameter is required"
    }


def test_list_tickets_equipment_not_found(client):
    response = client.get("/tickets?equipmentId=does-not-exist")
    assert response.status_code == 404
    assert response.get_json() == {"message": "Equipment not found"}


def test_create_ticket(client, store):
    load_locker(store)
    response = client.post(
        "/tickets",
        json={"name": "Alex", "quantity": 1, "equipmentId": GLOVES.equipment_id},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert len(body["ticketId"]) == 8
    assert body["name"] == "Alex"
    assert body["quantity"] == 1
    assert body["equipmentId"] == GLOVES.equipment_id
    assert body["createdAt"].endswith("Z")
    assert response.headers["Location"] == f"/tickets/{body['ticketId']}"

    locker = client.get("/equipment")
    gloves = next(item for item in locker.get_json() if item["itemName"] == "Gloves")
    assert gloves["total"] == 12
    assert gloves["available"] == 11


def test_create_ticket_conflict_when_none_available(client, store):
    load_locker(store)
    response = client.post(
        "/tickets",
        json={"name": "Alex", "quantity": 1, "equipmentId": BATS.equipment_id},
    )
    assert response.status_code == 409
    assert response.get_json() == {
        "message": "quantity is greater than the available quantity"
    }


def test_create_ticket_equipment_not_found(client):
    response = client.post(
        "/tickets",
        json={"name": "Alex", "quantity": 1, "equipmentId": "does-not-exist"},
    )
    assert response.status_code == 404
    assert response.get_json() == {"message": "Equipment not found"}


def test_create_ticket_bad_request(client, store):
    load_locker(store)
    response = client.post(
        "/tickets",
        json={"name": "Alex", "quantity": 0, "equipmentId": GLOVES.equipment_id},
    )
    assert response.status_code == 400
    assert response.get_json() == {"message": "quantity must be at least 1"}


def test_get_ticket(client, store):
    load_locker(store)
    response = client.get(f"/tickets/{LUCAS_TICKET.ticket_id}")
    assert response.status_code == 200
    assert response.get_json() == {
        "ticketId": "k7m2xq9p",
        "createdAt": "2026-07-28T12:15:00.000Z",
        "name": "Lucas",
        "quantity": 2,
        "equipmentId": "k7m1xq9p",
    }


def test_get_ticket_not_found(client):
    response = client.get("/tickets/does-not-exist")
    assert response.status_code == 404
    assert response.get_json() == {"message": "Ticket not found"}


def test_return_ticket(client, store):
    load_locker(store)
    response = client.delete(f"/tickets/{LUCAS_TICKET.ticket_id}")
    assert response.status_code == 204
    assert response.data == b""

    missing = client.get(f"/tickets/{LUCAS_TICKET.ticket_id}")
    assert missing.status_code == 404

    locker = client.get("/equipment")
    bats = next(item for item in locker.get_json() if item["itemName"] == "Bats")
    assert bats["total"] == 2
    assert bats["available"] == 2


def test_return_ticket_not_found(client):
    response = client.delete("/tickets/does-not-exist")
    assert response.status_code == 404
    assert response.get_json() == {"message": "Ticket not found"}
