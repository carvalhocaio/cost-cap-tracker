"""Tests for Rich-based CLI output formatting."""

import io
from datetime import date

from rich.console import Console

from cost_cap_tracker.domain.budget import BudgetStatus
from cost_cap_tracker.domain.expense import Expense
from cost_cap_tracker.infrastructure.cli import output


def make_console() -> Console:
    return Console(file=io.StringIO(), width=200)


class TestPrintAddSuccess:
    def test_includes_the_new_id(self):
        console = make_console()

        output.print_add_success(console, 1)

        assert "Expense added successfully (ID: 1)" in console.file.getvalue()


class TestPrintExpenses:
    def test_prints_placeholder_when_empty(self):
        console = make_console()

        output.print_expenses(console, [])

        assert "No expenses yet." in console.file.getvalue()

    def test_prints_a_table_with_expense_data(self):
        console = make_console()
        expenses = [
            Expense(
                id=1,
                description="Wind tunnel session",
                amount=250_000,
                category="Chassis & Aero",
                date=date(2026, 3, 1),
            )
        ]

        output.print_expenses(console, expenses)

        text = console.file.getvalue()
        assert "Wind tunnel session" in text
        assert "Chassis & Aero" in text
        assert "2026-03-01" in text
        assert "$250,000.00" in text


class TestPrintBudgetStatus:
    def test_prints_breach_message_with_flag(self):
        console = make_console()
        status = BudgetStatus(month=3, total=600_000, cap=500_000)

        output.print_budget_status(console, status)

        text = console.file.getvalue()
        assert "🚩" in text
        assert "breach" in text
        assert "March" in text
        assert "over by $100,000.00" in text

    def test_prints_remaining_message_when_under_cap(self):
        console = make_console()
        status = BudgetStatus(month=3, total=400_000, cap=500_000)

        output.print_budget_status(console, status)

        text = console.file.getvalue()
        assert "🚩" not in text
        assert "$100,000.00 remaining" in text
