# Development Setup and Startup

This project is a Flask app that uses MySQL and a Python 3.12+ environment. The app is started with the Flask entry point in `src/equipment/app.py`, and it expects environment settings from a `.env` file before it can connect to the database.

## Prerequisites

Before you start, make sure you have:

- Python 3.12 or newer
- `pip` for installing Python packages
- A local MySQL server available
- A terminal with access to the repository root

The project declares its Python requirement in `setup.py` and its runtime packages in `requirements.txt`.

## 1. Create and activate a virtual environment

From the project root:

```bash
cd /path/to/sport-equipment-monolith
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Upgrade pip and install dependencies

Install the required Python libraries:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

This installs the Flask app, database client, testing tools, and other dependencies required for development and testing.

## 3. Configure environment settings

Create a `.env` file in the project root based on the example template:

```bash
cp config/example.env .env
```

The example file contains the required MySQL settings:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=<replace with your password>
MYSQL_DATABASE=equipment
```

Update the values to match your local database setup. The app loads these values automatically via `python-dotenv`.

> The app will fail to start if any required setting is missing.

## 4. Start the database

Make sure your MySQL server is running before starting the app in a new terminal.
```bash
mysql -u root -p
```

If you are using a fresh local database, create the required tables in virtual environment:

```bash
python scripts/create_table.py
python scripts/seed.py

```

This script creates the `Equipment` and `Ticket` tables in the configured database.

If you need to reset the schema later, you can also delete the tables with:

```bash
python scripts/delete_table.py
```

To verify `Equipment` and `Ticket` tables are in database in MySQL terminal.

```bash
USE equipment;
SHOW TABLES;
```

## 5. Start the app

Once the database is available and the environment is configured, run in virtual environment:

```bash
python -m equipment.app
```

This starts the Flask app on port `5000` by default.

Open the app in a browser at:

```text
http://127.0.0.1:5000
```

The app serves the equipment UI and API endpoints from the Flask server.

## 6. Run tests

The repository uses `pytest` for automated tests. From the project root after installing dependencies:

```bash
pytest -q
```

This is the standard verification command for the project. Unit tests use an in-memory SQLite database, so they do not require a running MySQL server. The application itself, however, still expects the configured MySQL connection when running the full app.

## Useful notes

- The repo expects the project root to be the working directory when you run commands.
- If you see a database connection error, check that:
  - the database is running,
  - the `.env` file is populated correctly,
  - the tables were created with `python scripts/create_table.py`.
- If you are working in a fresh environment, reinstall dependencies after activating the venv:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Typical quick-start sequence

```bash
cd /path/to/sport-equipment-monolith
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
cp config/example.env .env
python scripts/create_table.py
python scripts/seed.py
python -m equipment.app
```

This is the normal local startup flow for the project.
