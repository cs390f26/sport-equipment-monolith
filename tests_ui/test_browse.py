"""Browse equipment when the locker already has data."""

from sample_data import BATS


def test_list_shows_available_and_total(page, sample_locker):
    page.goto("/")

    bats = page.locator(".equipment-btn").filter(has_text="Bats")
    bats.wait_for()
    assert bats.locator(".qty b").inner_text() == "0/2"

    helmets = page.locator(".equipment-btn").filter(has_text="Helmets")
    assert helmets.locator(".qty b").inner_text() == "9/10"
    baseballs = page.locator(".equipment-btn").filter(has_text="Baseballs")
    assert baseballs.locator(".qty b").inner_text() == "21/24"
    gloves = page.locator(".equipment-btn").filter(has_text="Gloves")
    assert gloves.locator(".qty b").inner_text() == "12/12"


def test_list_shows_items_in_name_order(page, sample_locker):
    page.goto("/")
    names = page.locator(".equipment-btn .item-name")
    names.first.wait_for()
    assert names.all_inner_texts() == [
        "Baseballs",
        "Bases",
        "Bats",
        "Catcher's gear",
        "Gloves",
        "Helmets",
    ]


def test_item_link_opens_that_items_tickets(page, sample_locker):
    page.goto("/")
    page.locator(".equipment-btn").filter(has_text="Bats").click()

    page.wait_for_url(f"**/tickets?equipmentId={BATS.equipment_id}")
    page.get_by_role("heading", name="Bats").wait_for()
