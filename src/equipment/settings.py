"""Load .env and require the settings this project needs to reach Aurora."""

import os

from dotenv import load_dotenv

# AURORA_PASSWORD may be an empty string (local MySQL with no password).
REQUIRED_SETTINGS = (
    "AURORA_HOST",
    "AURORA_PORT",
    "AURORA_USER",
    "AURORA_PASSWORD",
    "AURORA_DATABASE",
)


def ensure_settings() -> dict[str, str]:
    """Load .env (if present) and require Aurora connection settings.

    Returns a dict of the required values. Raises RuntimeError if any required
    setting is missing. An empty AURORA_PASSWORD is allowed.
    """
    load_dotenv()
    missing = []
    for name in REQUIRED_SETTINGS:
        if name not in os.environ or (
            name != "AURORA_PASSWORD" and not os.environ.get(name)
        ):
            missing.append(name)
    if missing:
        raise RuntimeError(
            "Missing required settings in the environment / .env: "
            + ", ".join(missing)
        )
    return {name: os.environ[name] for name in REQUIRED_SETTINGS}
