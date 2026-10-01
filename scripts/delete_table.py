"""Drop the Equipment and Ticket tables in MySQL.

Prompts for confirmation unless -y is passed.
"""

import argparse
import sys

from equipment.db import DatabaseUnavailableError, EquipmentStorage
from equipment.settings import ensure_settings


def _confirm_delete() -> bool:
    answer = input(
        "Delete the Equipment and Ticket tables? This cannot be undone. [y/N] "
    ).strip().lower()
    return answer in ("y", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Drop the Equipment and Ticket tables."
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Delete without prompting.",
    )
    args = parser.parse_args()

    try:
        settings = ensure_settings()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    if not args.yes and not _confirm_delete():
        print("Cancelled.")
        return

    storage = EquipmentStorage.from_settings(settings)
    try:
        storage.drop_tables()
    except DatabaseUnavailableError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    finally:
        storage.close()

    print("Dropped Equipment and Ticket.")


if __name__ == "__main__":
    main()
