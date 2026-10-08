"""Load start data from data/sample-data.sql into MySQL.

The tables must already exist (python scripts/create_table.py).
CREATE TABLE statements in the SQL file are skipped.
"""

import sys
from pathlib import Path
from equipment.db import DatabaseUnavailableError, EquipmentStorage
from equipment.settings import ensure_settings

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_SQL = ROOT / "data" / "sample-data.sql"


def _insert_statements(sql_text: str) -> list[str]:
    """Return INSERT statements, ignoring CREATE TABLE."""
    statements = []
    for chunk in sql_text.split(";"):
        statement = chunk.strip()
        if statement.upper().startswith("INSERT"):
            statements.append(statement)
    return statements


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

    if not SAMPLE_SQL.is_file():
        print(f"Sample data file not found: {SAMPLE_SQL}", file=sys.stderr)
        sys.exit(1)

    statements = _insert_statements(SAMPLE_SQL.read_text())
    if not statements:
        print(f"No INSERT statements in {SAMPLE_SQL}", file=sys.stderr)
        sys.exit(1)

    storage = EquipmentStorage.from_settings(settings)
    try:
        storage.ping()
        if storage.list_equipment():
            if _ask_replace_or_quit() == "quit":
                print("Seeding stopped.")
                sys.exit(1)
            storage.clear_all()
        for statement in statements:
            storage._execute(statement, commit=True)
    except DatabaseUnavailableError as exc:
        print(
            "MySQL is missing or unreachable. "
            "Create the tables first: python scripts/create_table.py\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)
    finally:
        storage.close()

    print("Seeded start data from data/sample-data.sql.")


if __name__ == "__main__":
    main()
