"""Add equipment (and cancel / validation)."""


def test_add_gear_shows_new_item_on_the_list(page, locker_storage):
    page.goto("/equipment/new")

    page.locator('input[name="name"]').fill("Softball gloves")
    page.locator('input[name="quantity"]').fill("12")
    page.get_by_role("button", name="Add gear").click()

    page.wait_for_url("**/")
    row = page.locator(".equipment-btn").filter(has_text="Softball gloves")
    row.wait_for()
    assert row.locator(".qty b").inner_text() == "12/12"


def test_cancel_returns_to_equipment_list(page, locker_storage):
    page.goto("/equipment/new")
    page.locator('input[name="name"]').fill("Should not save")
    page.get_by_role("link", name="Cancel").click()

    page.wait_for_url("**/")
    page.get_by_role("link", name="Add gear").wait_for()
    assert page.get_by_text("Should not save").count() == 0


def test_add_gear_shows_error_when_name_missing(page, locker_storage):
    page.goto("/equipment/new")
    page.locator('input[name="quantity"]').fill("4")
    page.get_by_role("button", name="Add gear").click()

    error = page.locator("#form-error")
    error.wait_for()
    assert "name" in error.inner_text().lower()
    assert error.get_attribute("role") == "alert"
    assert "alert" in error.get_attribute("class").split()
    assert "/equipment/new" in page.url
