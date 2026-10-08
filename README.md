# Equipment

This is the monolithic implementation of the Equipment application. See the **specs** repository for the product specifications (use cases, API, data model, and related materials).

**Monolithic** here means Flask (HTTP API and browser UI) and MySQL (Aurora later) run together on a single machine.

## Documentation

| Doc                                      | Contents                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| [Development setup](docs/development.md) | Virtualenv, install, requirements, `.env`, MySQL, run the app, acceptance tests |
| [Deploy on EC2](docs/deploy.md)      | Security group, user data, systemd, debugging                                   |

## Quick start

- Create a virtual environment and install dependencies
- Configure `.env` from `config/example.env`
- Start MySQL locally and create the `Equipment` and `Tickets` tables
- Run `python -m equipment.app` and open [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

See [Development setup](docs/development.md) for full steps.
