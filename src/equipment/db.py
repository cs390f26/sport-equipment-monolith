import re
import sqlite3
import threading

import pymysql
from pymysql.err import IntegrityError

from equipment.types import (
    EquipmentData,
    TicketData,
    equipment_from_mapping,
    ticket_from_mapping,
)

# Same tables as the specs. Available quantity is not a column.
# MySQL uses InnoDB, which enforces the ticket foreign key.
EQUIPMENT_SQL = """
CREATE TABLE IF NOT EXISTS Equipment (
  equipmentId VARCHAR(32) PRIMARY KEY,
  itemName VARCHAR(64) NOT NULL,
  total INT NOT NULL
) ENGINE=InnoDB
"""

TICKET_SQL = """
CREATE TABLE IF NOT EXISTS Ticket (
  ticketId VARCHAR(32) PRIMARY KEY,
  createdAt VARCHAR(30) NOT NULL,
  name VARCHAR(64) NOT NULL,
  quantity INT NOT NULL,
  equipmentId VARCHAR(32) NOT NULL,
  FOREIGN KEY (equipmentId) REFERENCES Equipment (equipmentId)
) ENGINE=InnoDB
"""

# Same columns, without MySQL-only table options, for in-memory unit tests.
SQLITE_EQUIPMENT_SQL = """
CREATE TABLE IF NOT EXISTS Equipment (
  equipmentId VARCHAR(32) PRIMARY KEY,
  itemName VARCHAR(64) NOT NULL,
  total INT NOT NULL
)
"""

SQLITE_TICKET_SQL = """
CREATE TABLE IF NOT EXISTS Ticket (
  ticketId VARCHAR(32) PRIMARY KEY,
  createdAt VARCHAR(30) NOT NULL,
  name VARCHAR(64) NOT NULL,
  quantity INT NOT NULL,
  equipmentId VARCHAR(32) NOT NULL,
  FOREIGN KEY (equipmentId) REFERENCES Equipment (equipmentId)
)
"""

_DUPLICATE = 1062
_FOREIGN_KEY = {1452, 1216}
_DATABASE_NAME = re.compile(r"^[A-Za-z0-9_]+$")


class DatabaseUnavailableError(Exception):
    """Raised when MySQL or the tables cannot be used."""


class EquipmentAlreadyExistsError(Exception):
    """Raised when inserting an equipment id that is already stored."""


class EquipmentNotFoundError(Exception):
    """Raised when a ticket refers to an equipment id that is not stored."""


class TicketAlreadyExistsError(Exception):
    """Raised when inserting a ticket id that is already stored."""


class TicketNotFoundError(Exception):
    """Raised when deleting a ticket id that is not stored."""


class EquipmentStorage:
    """Stores equipment and tickets.

    The running app uses MySQL (from_settings). Flask serves requests on
    more than one thread, and a pymysql connection cannot be shared, so
    each thread keeps its own connection. Unit tests use in_memory(), an
    in-process database, so pytest does not need MySQL.
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        if not host:
            raise ValueError("host is required")
        if not user:
            raise ValueError("user is required")
        if not database:
            raise ValueError("database is required")
        if not _DATABASE_NAME.fullmatch(database):
            raise ValueError(
                "database must contain only letters, numbers, and underscores"
            )
        try:
            self._port = int(port)
        except (TypeError, ValueError) as exc:
            raise ValueError("port must be an integer") from exc

        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._local = threading.local()
        self._memory = False

    @classmethod
    def in_memory(cls) -> "EquipmentStorage":
        """Open a throwaway database for unit tests. Nothing is saved to disk."""
        storage = object.__new__(cls)
        storage._memory = True
        storage._database = "memory"
        storage._conn = sqlite3.connect(":memory:")
        storage._conn.row_factory = sqlite3.Row
        storage._conn.execute("PRAGMA foreign_keys = ON")
        return storage

    @classmethod
    def from_settings(cls, settings: dict[str, str]) -> "EquipmentStorage":
        """Build storage from ensure_settings() values."""
        return cls(
            host=settings["MYSQL_HOST"],
            port=int(settings["MYSQL_PORT"]),
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            database=settings["MYSQL_DATABASE"],
        )

    def close(self) -> None:
        """Close this thread's database connection if it is open."""
        if self._memory:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
            return
        connection = getattr(self._local, "conn", None)
        if connection is not None:
            connection.close()
            self._local.conn = None

    def ensure_database(self) -> None:
        """Create the MySQL database if it does not exist.

        Connects without selecting a database, so this works before the
        schema exists. No-op for the in-memory test database.
        """
        if self._memory:
            return
        try:
            connection = pymysql.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                connect_timeout=3,
                autocommit=True,
            )
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self._database}`")
            connection.close()
        except pymysql.MySQLError as exc:
            raise DatabaseUnavailableError(f"database unavailable: {exc}") from exc

    def create_schema(self) -> None:
        """Create Equipment and Ticket if they are not already there."""
        if self._memory:
            self._execute(SQLITE_EQUIPMENT_SQL, commit=True)
            self._execute(SQLITE_TICKET_SQL, commit=True)
            return
        self._execute(EQUIPMENT_SQL, commit=True)
        self._execute(TICKET_SQL, commit=True)

    def drop_tables(self) -> None:
        """Drop Ticket and Equipment if they exist."""
        self._execute("DROP TABLE IF EXISTS Ticket", commit=True)
        self._execute("DROP TABLE IF EXISTS Equipment", commit=True)

    def tables_exist(self) -> bool:
        """Return whether both Equipment and Ticket are in this database."""
        if self._memory:
            cursor = self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
            names = {row["name"].lower() for row in cursor.fetchall()}
            return {"equipment", "ticket"} <= names
        rows, _rowcount = self._execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            """,
            (self._database,),
            fetch=True,
        )
        names = set()
        for row in rows:
            table_name = row.get("table_name", row.get("TABLE_NAME"))
            if table_name:
                names.add(table_name.lower())
        return {"equipment", "ticket"} <= names

    def ping(self) -> None:
        """Check that MySQL is reachable and both tables exist.

        Raises DatabaseUnavailableError if the connection fails or a table
        is missing.
        """
        if not self.tables_exist():
            raise DatabaseUnavailableError("Equipment or Ticket table is missing")

    def clear_all(self) -> None:
        """Delete every ticket and equipment row.

        Used by acceptance tests to reset the database. Tickets go first so
        the foreign key is satisfied.
        """
        self._execute("DELETE FROM Ticket", commit=False)
        self._execute("DELETE FROM Equipment", commit=True)

    def add_equipment(self, equipment: EquipmentData) -> None:
        """Insert one equipment row.

        Raises EquipmentAlreadyExistsError if equipment_id is already stored.
        Raises DatabaseUnavailableError on other database failures.
        """
        try:
            self._execute(
                """
                INSERT INTO Equipment (equipmentId, itemName, total)
                VALUES (%s, %s, %s)
                """,
                (equipment.equipment_id, equipment.item_name, equipment.total),
                commit=True,
            )
        except (IntegrityError, sqlite3.IntegrityError) as exc:
            if _is_duplicate(exc):
                raise EquipmentAlreadyExistsError(
                    f"equipment {equipment.equipment_id!r} already exists"
                ) from exc
            raise DatabaseUnavailableError(f"database unavailable: {exc}") from exc

    def get_equipment(self, equipment_id: str) -> EquipmentData | None:
        """Return one equipment row, or None if it does not exist."""
        rows, _rowcount = self._execute(
            """
            SELECT equipmentId, itemName, total
            FROM Equipment
            WHERE equipmentId = %s
            """,
            (equipment_id,),
            fetch=True,
        )
        if not rows:
            return None
        return equipment_from_mapping(rows[0])

    def list_equipment(self) -> list[EquipmentData]:
        """Return every equipment row, unsorted."""
        rows, _rowcount = self._execute(
            "SELECT equipmentId, itemName, total FROM Equipment",
            fetch=True,
        )
        return [equipment_from_mapping(row) for row in rows]

    def add_ticket(self, ticket: TicketData) -> None:
        """Insert one ticket row.

        Raises TicketAlreadyExistsError if ticket_id is already stored.
        Raises EquipmentNotFoundError if equipment_id is not in Equipment.
        Raises DatabaseUnavailableError on other database failures.
        """
        try:
            self._execute(
                """
                INSERT INTO Ticket
                    (ticketId, createdAt, name, quantity, equipmentId)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    ticket.ticket_id,
                    ticket.created_at,
                    ticket.name,
                    ticket.quantity,
                    ticket.equipment_id,
                ),
                commit=True,
            )
        except (IntegrityError, sqlite3.IntegrityError) as exc:
            if _is_foreign_key(exc):
                raise EquipmentNotFoundError(
                    f"equipment {ticket.equipment_id!r} not found"
                ) from exc
            if _is_duplicate(exc):
                raise TicketAlreadyExistsError(
                    f"ticket {ticket.ticket_id!r} already exists"
                ) from exc
            raise DatabaseUnavailableError(f"database unavailable: {exc}") from exc

    def get_ticket(self, ticket_id: str) -> TicketData | None:
        """Return one ticket, or None if it does not exist."""
        rows, _rowcount = self._execute(
            """
            SELECT ticketId, createdAt, name, quantity, equipmentId
            FROM Ticket
            WHERE ticketId = %s
            """,
            (ticket_id,),
            fetch=True,
        )
        if not rows:
            return None
        return ticket_from_mapping(rows[0])

    def list_tickets(self, equipment_id: str) -> list[TicketData]:
        """Return open tickets for one equipment item, unsorted."""
        rows, _rowcount = self._execute(
            """
            SELECT ticketId, createdAt, name, quantity, equipmentId
            FROM Ticket
            WHERE equipmentId = %s
            """,
            (equipment_id,),
            fetch=True,
        )
        return [ticket_from_mapping(row) for row in rows]

    def delete_ticket(self, ticket_id: str) -> None:
        """Delete one ticket.

        Raises TicketNotFoundError if the id is not stored.
        Raises DatabaseUnavailableError on other database failures.
        """
        _rows, rowcount = self._execute(
            "DELETE FROM Ticket WHERE ticketId = %s",
            (ticket_id,),
            commit=True,
        )
        if rowcount == 0:
            raise TicketNotFoundError(f"ticket {ticket_id!r} not found")

    def _connect(self):
        """Return this thread's MySQL connection, opening one if needed."""
        connection = getattr(self._local, "conn", None)
        if connection is not None and connection.open:
            return connection
        try:
            connection = pymysql.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=3,
                charset="utf8mb4",
                autocommit=False,
            )
        except pymysql.MySQLError as exc:
            raise DatabaseUnavailableError(f"database unavailable: {exc}") from exc
        self._local.conn = connection
        return connection

    def _discard_mysql(self, connection) -> None:
        """Drop a connection a query left unusable."""
        try:
            connection.close()
        except pymysql.MySQLError:
            pass
        if getattr(self._local, "conn", None) is connection:
            self._local.conn = None

    def _execute(self, sql: str, params=None, *, commit: bool = False, fetch: bool = False):
        if self._memory:
            return self._execute_memory(sql, params, commit=commit, fetch=fetch)
        connection = self._connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall() if fetch else ()
                rowcount = cursor.rowcount
            if commit:
                connection.commit()
            return rows, rowcount
        except IntegrityError:
            connection.rollback()
            raise
        except pymysql.MySQLError as exc:
            self._discard_mysql(connection)
            raise DatabaseUnavailableError(f"database unavailable: {exc}") from exc
        except Exception:
            self._discard_mysql(connection)
            raise

    def _execute_memory(self, sql: str, params, *, commit: bool, fetch: bool):
        try:
            cursor = self._conn.execute(sql.replace("%s", "?"), params or ())
            rows = [dict(row) for row in cursor.fetchall()] if fetch else ()
            rowcount = cursor.rowcount
            if commit:
                self._conn.commit()
            return rows, rowcount
        except sqlite3.IntegrityError:
            self._conn.rollback()
            raise
        except sqlite3.Error as exc:
            raise DatabaseUnavailableError(f"database unavailable: {exc}") from exc


def _is_duplicate(exc: BaseException) -> bool:
    if isinstance(exc, IntegrityError) and exc.args and exc.args[0] == _DUPLICATE:
        return True
    return "unique" in str(exc).lower()


def _is_foreign_key(exc: BaseException) -> bool:
    if isinstance(exc, IntegrityError) and exc.args and exc.args[0] in _FOREIGN_KEY:
        return True
    return "foreign key" in str(exc).lower()
