"""Named sample rows for tests.

Values match scenario 1 in the specs sample data: a locker with three open
tickets. Available quantity is not stored. Bats are 0/2, Helmets are 9/10,
and Baseballs are 21/24. Gloves, Catcher's gear, and Bases are fully available.

SOFTBALL_GLOVES is the row added in the add-equipment scenario.
ALEX_TICKET is the Gloves borrow from the successful create-ticket scenario.
"""

from equipment.types import EquipmentData, TicketData

BATS = EquipmentData(equipment_id="k7m1xq9p", item_name="Bats", total=2)
GLOVES = EquipmentData(equipment_id="g4n8kp2w", item_name="Gloves", total=12)
HELMETS = EquipmentData(equipment_id="h2p6rt3c", item_name="Helmets", total=10)
BASEBALLS = EquipmentData(equipment_id="b9q4vs1b", item_name="Baseballs", total=24)
CATCHERS_GEAR = EquipmentData(
    equipment_id="c2t7yh5d",
    item_name="Catcher's gear",
    total=3,
)
BASES = EquipmentData(equipment_id="a8w3mn4f", item_name="Bases", total=4)
SOFTBALL_GLOVES = EquipmentData(
    equipment_id="s6f2gl8q",
    item_name="Softball gloves",
    total=12,
)

LUCAS_TICKET = TicketData(
    ticket_id="k7m2xq9p",
    created_at="2026-07-28T12:15:00.000Z",
    name="Lucas",
    quantity=2,
    equipment_id=BATS.equipment_id,
)
JORDAN_TICKET = TicketData(
    ticket_id="t9r3ab6k",
    created_at="2026-07-30T16:00:00.000Z",
    name="Jordan",
    quantity=3,
    equipment_id=BASEBALLS.equipment_id,
)
MAYA_TICKET = TicketData(
    ticket_id="n4p8wd2c",
    created_at="2026-08-03T14:30:00.000Z",
    name="Maya",
    quantity=1,
    equipment_id=HELMETS.equipment_id,
)
ALEX_TICKET = TicketData(
    ticket_id="m3n8kp2w",
    created_at="2026-08-05T10:00:00.000Z",
    name="Alex",
    quantity=1,
    equipment_id=GLOVES.equipment_id,
)

LOCKER_EQUIPMENT = [BATS, GLOVES, HELMETS, BASEBALLS, CATCHERS_GEAR, BASES]
LOCKER_TICKETS = [MAYA_TICKET, JORDAN_TICKET, LUCAS_TICKET]


def load_locker(store) -> None:
    """Insert scenario 1 equipment and tickets."""
    for equipment in LOCKER_EQUIPMENT:
        store.add_equipment(equipment)
    for ticket in LOCKER_TICKETS:
        store.add_ticket(ticket)
