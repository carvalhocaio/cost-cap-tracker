"""Presentation-only formatting for expenses and budget status -- mirrors
output.rs, using Rich for semantic-colored terminal output. No business
logic, no I/O beyond the console it's given.
"""

import calendar

from rich.console import Console
from rich.table import Table

from cost_cap_tracker.domain.budget import BudgetStatus
from cost_cap_tracker.domain.expense import Expense

_CLOSE_TO_CAP_RATIO = 0.1


def print_add_success(console: Console, expense_id: int) -> None:
    console.print(f"[green]Expense added successfully (ID: {expense_id})[/green]")


def print_expenses(console: Console, expenses: list[Expense]) -> None:
    if not expenses:
        console.print("[dim]No expenses yet.[/dim]")
        return

    table = Table()
    table.add_column("ID", justify="right")
    table.add_column("Date")
    table.add_column("Category")
    table.add_column("Description")
    table.add_column("Amount", justify="right")
    for expense in expenses:
        table.add_row(
            str(expense.id),
            expense.date.isoformat(),
            expense.category,
            expense.description,
            f"${expense.amount:,.2f}",
        )
    console.print(table)


def print_budget_status(console: Console, status: BudgetStatus) -> None:
    month_name = calendar.month_name[status.month]
    if status.is_breach():
        overage = status.total - status.cap
        console.print(
            f"[bold red]🚩 Cost cap breach for {month_name}: spent "
            f"${status.total:,.2f} of ${status.cap:,.2f} cap "
            f"(over by ${overage:,.2f})[/bold red]"
        )
        return

    remaining = status.remaining()
    style = "yellow" if remaining <= status.cap * _CLOSE_TO_CAP_RATIO else "green"
    console.print(
        f"[{style}]Cost cap for {month_name}: spent ${status.total:,.2f} of "
        f"${status.cap:,.2f} cap (${remaining:,.2f} remaining)[/{style}]"
    )
