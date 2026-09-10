"""Orchestrates expense use cases (add/update/delete/list/summary/
set-budget/export), wiring pure domain rules to the ExpenseRepository
port. Contains no SQL; touches the filesystem only for CSV export.
"""

import csv
from dataclasses import dataclass
from datetime import date

from cost_cap_tracker.domain.budget import BudgetStatus
from cost_cap_tracker.domain.expense import DEFAULT_CATEGORY, Expense
from cost_cap_tracker.errors import (
    EmptyUpdateError,
    ExportError,
    InvalidAmountError,
    InvalidCapError,
    InvalidMonthError,
)
from cost_cap_tracker.infrastructure.repository import ExpenseRepository

_CSV_HEADER = ("id", "date", "category", "description", "amount")


@dataclass(frozen=True, slots=True)
class AddOutcome:
    id: int
    budget_status: BudgetStatus | None


class ExpenseService:
    def __init__(self, repository: ExpenseRepository) -> None:
        self._repository = repository

    def add(
        self, description: str, amount: float, category: str | None = None
    ) -> AddOutcome:
        """Validates amount > 0, inserts with today's date, and -- if a
        cap is set for the current month -- returns how the month now
        stands against it.
        """
        if amount <= 0:
            raise InvalidAmountError
        resolved_category = category if category is not None else DEFAULT_CATEGORY
        today = date.today()
        expense_id = self._repository.insert(
            description, amount, resolved_category, today
        )

        cap = self._repository.get_budget(today.month)
        budget_status = None
        if cap is not None:
            total = self._repository.total(today.month)
            budget_status = BudgetStatus(month=today.month, total=total, cap=cap)

        return AddOutcome(id=expense_id, budget_status=budget_status)

    def update(
        self,
        expense_id: int,
        description: str | None = None,
        amount: float | None = None,
        category: str | None = None,
    ) -> None:
        """Validates that at least one field changes and, if amount is
        given, that it is positive. Raises NotFoundError (propagated from
        the repository) if expense_id doesn't exist.
        """
        if description is None and amount is None and category is None:
            raise EmptyUpdateError
        if amount is not None and amount <= 0:
            raise InvalidAmountError
        self._repository.update(expense_id, description, amount, category)

    def delete(self, expense_id: int) -> None:
        """Raises NotFoundError (from the repository) if missing."""
        self._repository.delete(expense_id)

    def list(self, category: str | None = None) -> list[Expense]:
        return self._repository.list(category)

    def summary(self, month: int | None = None) -> float:
        """Total spend, optionally scoped to `month` of the current
        year. Raises InvalidMonthError if month is out of 1-12.
        """
        if month is not None and not (1 <= month <= 12):
            raise InvalidMonthError
        return self._repository.total(month)

    def set_budget(self, month: int, cap: float) -> None:
        """Raises InvalidMonthError / InvalidCapError on out-of-range
        month or non-positive cap.
        """
        if not (1 <= month <= 12):
            raise InvalidMonthError
        if cap <= 0:
            raise InvalidCapError
        self._repository.set_budget(month, cap)

    def export_csv(self, path: str) -> int:
        """Exports every expense to `path` as CSV and returns the row
        count. Wraps OSError/csv.Error into ExportError.
        """
        expenses = self._repository.list(None)
        try:
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(_CSV_HEADER)
                for expense in expenses:
                    writer.writerow(
                        (
                            expense.id,
                            expense.date.isoformat(),
                            expense.category,
                            expense.description,
                            f"{expense.amount:.2f}",
                        )
                    )
        except (OSError, csv.Error) as error:
            raise ExportError(error) from error
        return len(expenses)
