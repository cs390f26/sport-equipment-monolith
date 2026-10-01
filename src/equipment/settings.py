"""Load .env and require the settings this project needs to reach MySQL."""

import os

from dotenv import load_dotenv

# MYSQL_PASSWORD may be an empty string (local MySQL with no password).
REQUIRED_SETTINGS = (
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
)


def ensure_settings() -> dict[str, str]:
    """Load .env (if present) and require MySQL connection settings.

    Returns a dict of the required values. Raises RuntimeError if any required
    setting is missing. An empty MYSQL_PASSWORD is allowed.
    """
    load_dotenv()
    missing = []
    for name in REQUIRED_SETTINGS:
        if name not in os.environ or (
            name != "MYSQL_PASSWORD" and not os.environ.get(name)
        ):
            missing.append(name)
    if missing:
        raise RuntimeError(
            "Missing required settings in the environment / .env: "
            + ", ".join(missing)
        )
    return {name: os.environ[name] for name in REQUIRED_SETTINGS}
