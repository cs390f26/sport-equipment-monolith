"""Create a borrow ticket (and cancel / validation)."""

from sample_data import BATS, GLOVES


def test_create_ticket_shows_borrower_on_the_item_list(page, sample_locker):
    page.goto(f"/tickets/new?equipmentId={GLOVES.equipment_id}")

    page.get_by_role("heading", name="Borrow equipment").wait_for()
    assert page.locator(".item-name").filter(has_text="Gloves").is_visible()
    page.locator('input[name="name"]').fill("Alex")
    page.locator('input[name="quantity"]').fill("1")
    page.get_by_role("button", name="Create ticket").click()

    page.wait_for_url(f"**/tickets?equipmentId={GLOVES.equipment_id}")
    row = page.locator(".ticket-row").filter(has_text="Alex")
    row.wait_for()
    assert row.get_by_text("Qty 1").is_visible()


def test_cancel_returns_to_open_tickets(page, sample_locker):
    page.goto(f"/tickets/new?equipmentId={GLOVES.equipment_id}")
    page.locator('input[name="name"]').fill("Alex")
    page.locator('input[name="quantity"]').fill("1")
    page.get_by_role("link", name="Cancel").click()

    page.wait_for_url(f"**/tickets?equipmentId={GLOVES.equipment_id}")
    assert page.get_by_text("Alex").count() == 0


def test_create_ticket_shows_error_when_none_are_available(page, sample_locker):
    page.goto(f"/tickets/new?equipmentId={BATS.equipment_id}")
    page.locator('input[name="name"]').fill("Alex")
    page.locator('input[name="quantity"]').fill("1")
    page.get_by_role("button", name="Create ticket").click()

    error = page.locator("#form-error")
    error.wait_for()
    assert "available" in error.inner_text().lower()
    assert error.get_attribute("role") == "alert"
    assert "alert" in error.get_attribute("class").split()
    assert f"equipmentId={BATS.equipment_id}" in page.url


def test_create_ticket_shows_error_when_name_missing(page, sample_locker):
    page.goto(f"/tickets/new?equipmentId={GLOVES.equipment_id}")
    page.locator('input[name="quantity"]').fill("1")
    page.get_by_role("button", name="Create ticket").click()

    error = page.locator("#form-error")
    error.wait_for()
    assert "name" in error.inner_text().lower()
    assert "/tickets/new" in page.url
