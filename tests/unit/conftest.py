"""Shared test fixtures."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from cost_cap_tracker.domain.expense import Expense
from cost_cap_tracker.errors import NotFoundError


class FakeExpenseRepository:
    """In-memory stand-in for ExpenseRepository -- lets ExpenseService be
    unit-tested without touching SQLite."""

    def __init__(self) -> None:
        self._rows: dict[int, Expense] = {}
        self._next_id = 1
        self._budgets: dict[int, float] = {}

    def insert(
        self, description: str, amount: float, category: str, expense_date: date
    ) -> int:
        expense_id = self._next_id
        self._next_id += 1
        self._rows[expense_id] = Expense(
            id=expense_id,
            description=description,
            amount=amount,
            category=category,
            date=expense_date,
        )
        return expense_id

    def update(
        self,
        expense_id: int,
        description: str | None,
        amount: float | None,
        category: str | None,
    ) -> None:
        expense = self._rows.get(expense_id)
        if expense is None:
            raise NotFoundError(expense_id)

        changes = {}
        if description is not None:
            changes["description"] = description
        if amount is not None:
            changes["amount"] = amount
        if category is not None:
            changes["category"] = category
        self._rows[expense_id] = replace(expense, **changes)

    def delete(self, expense_id: int) -> None:
        if expense_id not in self._rows:
            raise NotFoundError(expense_id)
        del self._rows[expense_id]

    def list(self, category: str | None = None) -> list[Expense]:
        expenses = self._rows.values()
        if category is not None:
            expenses = (
                expense
                for expense in expenses
                if expense.category.lower() == category.lower()
            )
        return sorted(
            expenses, key=lambda expense: (expense.date, expense.id), reverse=True
        )

    def total(self, month: int | None = None) -> float:
        year = date.today().year
        return sum(
            expense.amount
            for expense in self._rows.values()
            if expense.date.year == year
            and (month is None or expense.date.month == month)
        )

    def set_budget(self, month: int, cap: float) -> None:
        self._budgets[month] = cap

    def get_budget(self, month: int) -> float | None:
        return self._budgets.get(month)


@pytest.fixture
def fake_repository() -> FakeExpenseRepository:
    return FakeExpenseRepository()
