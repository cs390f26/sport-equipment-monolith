"""View open tickets for the equipment item that was pressed."""

from sample_data import BATS, LUCAS_TICKET


def test_bats_lists_only_lucas(page, sample_locker):
    page.goto(f"/tickets?equipmentId={BATS.equipment_id}")

    page.get_by_role("heading", name="Bats").wait_for()
    row = page.locator(".ticket-row").filter(has_text="Lucas")
    row.wait_for()
    assert row.get_by_text("Qty 2").is_visible()
    assert page.get_by_text("Maya").count() == 0
    assert page.get_by_text("Jordan").count() == 0
    assert page.get_by_role("link", name="Add ticket").is_visible()


def test_ticket_row_opens_return_page(page, sample_locker):
    page.goto(f"/tickets?equipmentId={BATS.equipment_id}")
    page.locator(".ticket-row").filter(has_text="Lucas").click()

    page.wait_for_url(f"**/tickets/{LUCAS_TICKET.ticket_id}")
    page.get_by_role("heading", name=f"Ticket {LUCAS_TICKET.ticket_id}").wait_for()


def test_add_ticket_link_opens_create_page(page, sample_locker):
    page.goto(f"/tickets?equipmentId={BATS.equipment_id}")
    page.get_by_role("link", name="Add ticket").click()

    page.wait_for_url(f"**/tickets/new?equipmentId={BATS.equipment_id}")
    page.get_by_role("heading", name="Borrow equipment").wait_for()
