"""Tests for the CLI Session dispatch loop, wired against
ExpenseService(fake_repository) with captured Rich consoles instead of
real stdin/stdout."""

import io
from datetime import date

from rich.console import Console

from cost_cap_tracker.application.expense_service import ExpenseService
from cost_cap_tracker.infrastructure.cli.session import Session


def make_session(fake_repository):
    console = Console(file=io.StringIO(), width=200)
    error_console = Console(file=io.StringIO(), width=200)
    service = ExpenseService(fake_repository)
    session = Session(service, console=console, error_console=error_console)
    return session, console, error_console


class TestAdd:
    def test_prints_success_with_new_id(self, fake_repository):
        session, console, _ = make_session(fake_repository)

        code = session.run(["add", "--description", "Wind tunnel", "--amount", "1"])

        assert code == 0
        assert "Expense added successfully (ID: 1)" in console.file.getvalue()

    def test_prints_budget_status_when_cap_is_set(self, fake_repository):
        session, console, _ = make_session(fake_repository)
        session.run(["set-budget", "--month", str(date.today().month), "--cap", "1"])

        code = session.run(["add", "--description", "Over cap", "--amount", "2"])

        assert code == 0
        assert "🚩" in console.file.getvalue()

    def test_prints_nothing_extra_when_no_cap_is_set(self, fake_repository):
        session, console, _ = make_session(fake_repository)

        session.run(["add", "--description", "x", "--amount", "1"])

        assert "cap" not in console.file.getvalue().lower()


class TestUpdateAndDelete:
    def test_update_prints_success_message(self, fake_repository):
        session, console, _ = make_session(fake_repository)
        session.run(["add", "--description", "x", "--amount", "1"])

        code = session.run(["update", "--id", "1", "--amount", "2"])

        assert code == 0
        assert "Expense updated successfully" in console.file.getvalue()

    def test_delete_prints_success_message(self, fake_repository):
        session, console, _ = make_session(fake_repository)
        session.run(["add", "--description", "x", "--amount", "1"])

        code = session.run(["delete", "--id", "1"])

        assert code == 0
        assert "Expense deleted successfully" in console.file.getvalue()


class TestList:
    def test_prints_a_table(self, fake_repository):
        session, console, _ = make_session(fake_repository)
        session.run(["add", "--description", "Wind tunnel", "--amount", "1"])

        code = session.run(["list"])

        assert code == 0
        assert "Wind tunnel" in console.file.getvalue()

    def test_prints_placeholder_when_empty(self, fake_repository):
        session, console, _ = make_session(fake_repository)

        session.run(["list"])

        assert "No expenses yet." in console.file.getvalue()


class TestSummary:
    def test_prints_overall_total_with_no_month(self, fake_repository):
        session, console, _ = make_session(fake_repository)
        session.run(["add", "--description", "x", "--amount", "1"])

        session.run(["summary"])

        assert "Total expenses: $1.00" in console.file.getvalue()

    def test_prints_month_name_when_scoped(self, fake_repository):
        session, console, _ = make_session(fake_repository)

        session.run(["summary", "--month", "12"])

        assert "Total expenses for December: $0.00" in console.file.getvalue()


class TestSetBudget:
    def test_prints_the_cap_with_resolved_month_name(self, fake_repository):
        session, console, _ = make_session(fake_repository)

        code = session.run(["set-budget", "--month", "1", "--cap", "500"])

        assert code == 0
        assert "Cost cap for January set to $500.00" in console.file.getvalue()


class TestExport:
    def test_prints_row_count_and_path(self, fake_repository, tmp_path):
        session, console, _ = make_session(fake_repository)
        session.run(["add", "--description", "x", "--amount", "1"])
        output_path = str(tmp_path / "out.csv")

        code = session.run(["export", "--output", output_path])

        assert code == 0
        assert f"Exported 1 expense(s) to {output_path}" in console.file.getvalue()


class TestCategories:
    def test_prints_all_suggested_categories(self, fake_repository):
        session, console, _ = make_session(fake_repository)

        session.run(["categories"])

        text = console.file.getvalue()
        for category in [
            "Power Unit",
            "Chassis & Aero",
            "Personnel",
            "Logistics",
            "CapEx",
            "General",
        ]:
            assert category in text


class TestErrorHandling:
    def test_app_error_prints_to_error_console_and_returns_one(self, fake_repository):
        session, _, error_console = make_session(fake_repository)

        code = session.run(["update", "--id", "99", "--amount", "1"])

        assert code == 1
        assert "Error:" in error_console.file.getvalue()
        assert "not found" in error_console.file.getvalue()

    def test_successful_command_returns_zero(self, fake_repository):
        session, _, _ = make_session(fake_repository)

        code = session.run(["categories"])

        assert code == 0
