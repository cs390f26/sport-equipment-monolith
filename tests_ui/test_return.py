"""Open a ticket and return the borrowed equipment."""

from sample_data import BATS, LUCAS_TICKET


def test_ticket_page_shows_borrower_item_and_quantity(page, sample_locker):
    page.goto(f"/tickets/{LUCAS_TICKET.ticket_id}")

    page.get_by_role("heading", name=f"Ticket {LUCAS_TICKET.ticket_id}").wait_for()
    details = page.locator(".detail-grid")
    assert details.get_by_text("Lucas").is_visible()
    assert details.get_by_text("Bats").is_visible()
    assert details.get_by_text("2", exact=True).is_visible()
    assert page.get_by_role("button", name="Return item").is_visible()
    assert page.get_by_role("link", name="Back to tickets").is_visible()


def test_return_removes_ticket_and_restores_bats(page, sample_locker):
    page.goto(f"/tickets/{LUCAS_TICKET.ticket_id}")
    page.get_by_role("button", name="Return item").click()

    page.wait_for_url(f"**/tickets?equipmentId={BATS.equipment_id}")
    assert page.get_by_text("Lucas").count() == 0

    page.goto("/")
    bats = page.locator(".equipment-btn").filter(has_text="Bats")
    bats.wait_for()
    assert bats.locator(".qty b").inner_text() == "2/2"


def test_back_leaves_the_ticket_open(page, sample_locker):
    page.goto(f"/tickets/{LUCAS_TICKET.ticket_id}")
    page.get_by_role("link", name="Back to tickets").click()

    page.wait_for_url(f"**/tickets?equipmentId={BATS.equipment_id}")
    assert page.get_by_text("Lucas").is_visible()


def test_unknown_ticket_shows_not_found(page, locker_storage):
    page.goto("/tickets/does-not-exist")
    error = page.locator("#page-error")
    error.wait_for()
    assert "not found" in error.inner_text().lower()
