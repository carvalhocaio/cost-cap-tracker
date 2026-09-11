# Cost Cap Tracker

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![uv](https://img.shields.io/badge/packaging-uv-de5fe9)
![pytest](https://img.shields.io/badge/tests-pytest-0a9edc)
![Ruff](https://img.shields.io/badge/lint%2Fformat-ruff-d7ff64)
![Rich](https://img.shields.io/badge/output-rich-ff69b4)

A personal expense tracker themed after F1's cost cap regulations — log
expenses, tag them with F1-flavored categories, set a monthly cost cap, and
get a breach warning when you go over it.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Development](#development)
- [Project structure](#project-structure)
- [Design notes](#design-notes)
- [Project origin](#project-origin)

## Features

- Add, update, delete, and list expenses, with optional category filtering
- Spending summary, overall or scoped to a month of the current year
- Monthly cost cap: expenses added past the cap print a 🚩 breach warning
- Export expenses to CSV
- Local persistence via SQLite (`vessel.db`), created on first run
- Semantic-colored terminal output (Rich): green for success, yellow for a
  cap getting close, red for a breach

| Command       | Description                                       |
|---------------|----------------------------------------------------|
| `add`         | Add a new expense                                   |
| `update`      | Update an existing expense (only given fields change) |
| `delete`      | Delete an expense by id                             |
| `list`        | List expenses, optionally filtered by category      |
| `summary`     | Show a spending summary, overall or for a month      |
| `set-budget`  | Set a monthly cost cap                               |
| `export`      | Export expenses to CSV                               |
| `categories`  | List suggested categories                            |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Usage

```bash
git clone https://github.com/carvalhocaio/cost-cap-tracker.git
cd cost-cap-tracker
uv run cost-cap <COMMAND> [OPTIONS]
```

![demo](assets/demo.gif)

> The GIF above is generated with [VHS](https://github.com/charmbracelet/vhs)
> from [`assets/demo.tape`](assets/demo.tape). Regenerate it locally with
> `vhs assets/demo.tape` (requires VHS <= 0.11.0 -- 0.12.0 has a rendering
> regression that silently produces no output).

### Commands

**Add an expense**
```bash
uv run cost-cap add --description "Wind tunnel session" --amount 250000 --category "Chassis & Aero"
```
`--category` defaults to `General` if omitted.

**Update an expense** (only passed fields change)
```bash
uv run cost-cap update --id 1 --amount 260000
```

**Delete an expense**
```bash
uv run cost-cap delete --id 1
```

**List expenses** (optionally filtered by category)
```bash
uv run cost-cap list
uv run cost-cap list --category "Personnel"
```

**Show a spending summary** (optionally scoped to a month of the current year)
```bash
uv run cost-cap summary
uv run cost-cap summary --month 3
```

**Set a monthly cost cap**
```bash
uv run cost-cap set-budget --month 3 --cap 500000
```
Adding an expense in a month with a cap set prints how much of the cap is
used (green, or yellow when getting close), or a 🚩 breach warning in red if
you've gone over.

**Export expenses to CSV**
```bash
uv run cost-cap export --output expenses.csv
```

**List suggested categories**
```bash
uv run cost-cap categories
```

## Development

```bash
uv sync                    # install runtime + dev dependencies
uv run pytest -v           # run tests
uv run ruff check .        # lint
uv run ruff format .       # format
```

Or the equivalent `make` shortcuts:

```bash
make sync
make test
make lint
make format
make check   # lint + format-check + test, the aggregate gate
```

## Project structure

```
src/cost_cap_tracker/
├── __main__.py                # composition root -- all wiring happens here
├── errors.py                  # AppError hierarchy, shared across layers
├── domain/                    # pure models: no I/O, no persistence
│   ├── expense.py              # Expense, DEFAULT_CATEGORY, SUGGESTED_CATEGORIES
│   └── budget.py                # BudgetStatus
├── application/                # use-case orchestration
│   └── expense_service.py       # ExpenseService
└── infrastructure/
    ├── repository.py            # ExpenseRepository Protocol (the port)
    ├── sqlite_repository.py      # SqliteRepository (the adapter)
    └── cli/
        ├── parser.py             # argparse subcommand definitions
        ├── output.py              # Rich-based table/status formatting
        └── session.py             # dispatch loop, the only layer touching the console
```

## Design notes

Dependencies point inward: `cli → application → domain`, and `domain`
depends on nothing. `ExpenseService` depends on the `ExpenseRepository`
Protocol in `infrastructure/repository.py`, not on SQLite directly, so
tests exercise it against an in-memory fake repository while
`infrastructure/sqlite_repository.py` is tested separately against a real
(temporary) SQLite database. Persistent state lives in a single SQLite
file, `vessel.db`, created in the working directory on first run — the name
is a small nod to Twenty One Pilots' debut album, *Vessel*. Rich is used
only in the `infrastructure/cli` layer, for presentation; it has no
influence on the domain or application logic.

## Project origin

Built as an implementation of the
[Expense Tracker](https://roadmap.sh/projects/expense-tracker) project from
[roadmap.sh](https://roadmap.sh), originally written in Rust and rewritten
in Python.
