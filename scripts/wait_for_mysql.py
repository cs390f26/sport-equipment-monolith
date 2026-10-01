"""Wait until MySQL accepts a connection (CI and systemd ExecStartPre)."""

import argparse
import sys
import time

import pymysql

from equipment.settings import ensure_settings


def wait_for_mysql(settings: dict[str, str], timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = "connection failed"
    while time.monotonic() < deadline:
        try:
            connection = pymysql.connect(
                host=settings["MYSQL_HOST"],
                port=int(settings["MYSQL_PORT"]),
                user=settings["MYSQL_USER"],
                password=settings["MYSQL_PASSWORD"],
                database=settings["MYSQL_DATABASE"],
                connect_timeout=1,
            )
            connection.close()
            return
        except pymysql.MySQLError as exc:
            # 1049: server is up, but the database has not been created yet.
            if exc.args and exc.args[0] == 1049:
                return
            last_error = str(exc)
            time.sleep(1)
    raise TimeoutError(
        f"MySQL did not become ready within {timeout_seconds}s "
        f"(host {settings['MYSQL_HOST']!r}). Details: {last_error}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wait until MySQL accepts a connection."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Seconds to wait before failing (default: 60).",
    )
    args = parser.parse_args()

    try:
        settings = ensure_settings()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    try:
        wait_for_mysql(settings, args.timeout)
    except TimeoutError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    print("MySQL is ready.")


if __name__ == "__main__":
    main()
