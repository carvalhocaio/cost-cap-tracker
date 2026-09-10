"""Persistence port: everything the application layer needs from storage,
and nothing more. ExpenseService depends on this Protocol, not on SQLite
directly -- swapping the backend later means writing a new adapter, with
zero changes to business logic.
"""

from datetime import date
from typing import Protocol

from cost_cap_tracker.domain.expense import Expense


class ExpenseRepository(Protocol):
    def insert(
        self, description: str, amount: float, category: str, expense_date: date
    ) -> int: ...

    def update(
        self,
        expense_id: int,
        description: str | None,
        amount: float | None,
        category: str | None,
    ) -> None: ...

    def delete(self, expense_id: int) -> None: ...

    def list(self, category: str | None = None) -> list[Expense]: ...

    def total(self, month: int | None = None) -> float: ...

    def set_budget(self, month: int, cap: float) -> None: ...

    def get_budget(self, month: int) -> float | None: ...
