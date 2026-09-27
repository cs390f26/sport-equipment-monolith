"""Browse equipment when the tables exist but have no rows yet."""


def test_empty_list_shows_add_gear_and_no_items(page, locker_storage):
    page.goto("/")

    page.get_by_role("link", name="Add gear").wait_for()
    page.get_by_role("heading", name="Available gear").wait_for()
    assert page.locator(".equipment-btn").count() == 0
