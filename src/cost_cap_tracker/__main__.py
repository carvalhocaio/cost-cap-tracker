"""Composition root: opens the SQLite repository, wires the expense
service, and hands control to the CLI session.

The database filename is a small nod to Twenty One Pilots' debut album --
a vessel being, quite literally, a container for something you carry
with you.
"""

import sys

from cost_cap_tracker.application.expense_service import ExpenseService
from cost_cap_tracker.errors import AppError
from cost_cap_tracker.infrastructure.cli.session import Session
from cost_cap_tracker.infrastructure.sqlite_repository import SqliteRepository

DB_PATH = "vessel.db"


def main() -> None:
    try:
        repository = SqliteRepository(DB_PATH)
    except AppError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    service = ExpenseService(repository)
    session = Session(service)
    sys.exit(session.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
