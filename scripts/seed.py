"""Load scenario 1 from the specs sample data into Aurora.

The tables must already exist (python scripts/create_table.py).
"""

import sys
from pathlib import Path

from equipment.db import DatabaseUnavailableError, EquipmentStorage
from equipment.settings import ensure_settings

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

from sample_data import load_locker


def _ask_replace_or_quit() -> str:
    while True:
        answer = input(
            "Equipment rows already exist. [r]eplace or [q]uit? "
        ).strip().lower()
        if answer in ("r", "replace"):
            return "replace"
        if answer in ("q", "quit"):
            return "quit"
        print("Please enter r or q.")


def main() -> None:
    try:
        settings = ensure_settings()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    storage = EquipmentStorage.from_settings(settings)
    try:
        storage.ping()
        if storage.list_equipment():
            if _ask_replace_or_quit() == "quit":
                print("Seeding stopped.")
                sys.exit(1)
            storage.clear_all()
        load_locker(storage)
    except DatabaseUnavailableError as exc:
        print(
            "Aurora is missing or unreachable. "
            "Create the tables first: python scripts/create_table.py\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)
    finally:
        storage.close()

    print("Seeded scenario 1 (browse equipment).")


if __name__ == "__main__":
    main()
