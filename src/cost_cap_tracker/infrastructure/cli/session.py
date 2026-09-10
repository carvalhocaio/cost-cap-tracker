"""Drives one CLI invocation: parses argv, dispatches to ExpenseService,
and prints results/errors. The only layer that touches the console for
command output (formatting itself is delegated to output.py)."""

import calendar

from rich.console import Console

from cost_cap_tracker.application.expense_service import ExpenseService
from cost_cap_tracker.domain.expense import SUGGESTED_CATEGORIES
from cost_cap_tracker.errors import AppError
from cost_cap_tracker.infrastructure.cli import output
from cost_cap_tracker.infrastructure.cli.parser import build_parser


class Session:
    def __init__(
        self,
        service: ExpenseService,
        console: Console | None = None,
        error_console: Console | None = None,
    ) -> None:
        self._service = service
        self._console = console if console is not None else Console()
        self._error_console = (
            error_console if error_console is not None else Console(stderr=True)
        )

    def run(self, argv: list[str]) -> int:
        args = build_parser().parse_args(argv)
        try:
            self._dispatch(args)
        except AppError as error:
            self._error_console.print(f"[bold red]Error:[/bold red] {error}")
            return 1
        return 0

    def _dispatch(self, args) -> None:
        match args.command:
            case "add":
                outcome = self._service.add(
                    args.description, args.amount, args.category
                )
                output.print_add_success(self._console, outcome.id)
                if outcome.budget_status is not None:
                    output.print_budget_status(self._console, outcome.budget_status)
            case "update":
                self._service.update(
                    args.id, args.description, args.amount, args.category
                )
                self._console.print("[green]Expense updated successfully[/green]")
            case "delete":
                self._service.delete(args.id)
                self._console.print("[green]Expense deleted successfully[/green]")
            case "list":
                output.print_expenses(self._console, self._service.list(args.category))
            case "summary":
                total = self._service.summary(args.month)
                if args.month is not None:
                    month_name = calendar.month_name[args.month]
                    self._console.print(
                        f"Total expenses for {month_name}: ${total:,.2f}"
                    )
                else:
                    self._console.print(f"Total expenses: ${total:,.2f}")
            case "set-budget":
                self._service.set_budget(args.month, args.cap)
                month_name = calendar.month_name[args.month]
                self._console.print(
                    f"[green]Cost cap for {month_name} set to ${args.cap:,.2f}[/green]"
                )
            case "export":
                count = self._service.export_csv(args.output)
                self._console.print(f"Exported {count} expense(s) to {args.output}")
            case "categories":
                self._console.print("Suggested categories:")
                for category in SUGGESTED_CATEGORIES:
                    self._console.print(f"  - {category}")
