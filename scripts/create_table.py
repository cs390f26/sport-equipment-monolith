"""Create the Equipment and Ticket tables in Aurora.

Fails if both tables already exist. To reset, run delete_table.py first.
"""

import sys

from equipment.db import DatabaseUnavailableError, EquipmentStorage
from equipment.settings import ensure_settings


def main() -> None:
    try:
        settings = ensure_settings()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    storage = EquipmentStorage.from_settings(settings)
    try:
        storage.ensure_database()
        if storage.tables_exist():
            print(
                "Equipment and Ticket tables already exist. "
                "Delete them first if you want to recreate: "
                "python scripts/delete_table.py",
                file=sys.stderr,
            )
            sys.exit(1)
        storage.create_schema()
    except DatabaseUnavailableError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    finally:
        storage.close()

    print("Created Equipment and Ticket.")


if __name__ == "__main__":
    main()
