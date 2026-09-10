"""Tests for ExpenseService, exercised against FakeExpenseRepository so
no test here touches SQLite."""

from datetime import date

import pytest

from cost_cap_tracker.application.expense_service import ExpenseService
from cost_cap_tracker.domain.expense import DEFAULT_CATEGORY
from cost_cap_tracker.errors import (
    EmptyUpdateError,
    ExportError,
    InvalidAmountError,
    InvalidCapError,
    InvalidMonthError,
    NotFoundError,
)


@pytest.fixture
def service(fake_repository):
    return ExpenseService(fake_repository)


class TestAdd:
    def test_returns_the_new_expense_id(self, service):
        outcome = service.add("Wind tunnel session", 250_000)

        assert outcome.id == 1

    def test_defaults_category_when_omitted(self, service, fake_repository):
        service.add("Wind tunnel session", 250_000)

        [expense] = fake_repository.list()
        assert expense.category == DEFAULT_CATEGORY

    def test_keeps_the_given_category(self, service, fake_repository):
        service.add("Wind tunnel session", 250_000, category="Chassis & Aero")

        [expense] = fake_repository.list()
        assert expense.category == "Chassis & Aero"

    def test_rejects_zero_amount(self, service):
        with pytest.raises(InvalidAmountError):
            service.add("Wind tunnel session", 0)

    def test_rejects_negative_amount(self, service):
        with pytest.raises(InvalidAmountError):
            service.add("Wind tunnel session", -1)

    def test_no_budget_status_when_no_cap_set(self, service):
        outcome = service.add("Wind tunnel session", 250_000)

        assert outcome.budget_status is None

    def test_budget_status_when_under_cap(self, service):
        month = date.today().month
        service.set_budget(month, 500_000)

        outcome = service.add("Wind tunnel session", 250_000)

        assert outcome.budget_status.is_breach() is False
        assert outcome.budget_status.total == 250_000

    def test_budget_status_when_over_cap(self, service):
        month = date.today().month
        service.set_budget(month, 100_000)

        outcome = service.add("Wind tunnel session", 250_000)

        assert outcome.budget_status.is_breach() is True


class TestUpdate:
    def test_updates_only_given_fields(self, service, fake_repository):
        outcome = service.add("Wind tunnel session", 250_000, category="General")

        service.update(outcome.id, amount=260_000)

        [expense] = fake_repository.list()
        assert expense.amount == 260_000
        assert expense.description == "Wind tunnel session"
        assert expense.category == "General"

    def test_rejects_update_with_no_fields(self, service):
        outcome = service.add("Wind tunnel session", 250_000)

        with pytest.raises(EmptyUpdateError):
            service.update(outcome.id)

    def test_rejects_non_positive_amount(self, service):
        outcome = service.add("Wind tunnel session", 250_000)

        with pytest.raises(InvalidAmountError):
            service.update(outcome.id, amount=0)

    def test_propagates_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.update(99, amount=1)


class TestDelete:
    def test_deletes_an_existing_expense(self, service, fake_repository):
        outcome = service.add("Wind tunnel session", 250_000)

        service.delete(outcome.id)

        assert fake_repository.list() == []

    def test_propagates_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.delete(99)


class TestList:
    def test_lists_everything_with_no_filter(self, service):
        service.add("Wind tunnel session", 250_000, category="Chassis & Aero")
        service.add("Driver salary", 1_000_000, category="Personnel")

        assert len(service.list()) == 2

    def test_filters_by_category(self, service):
        service.add("Wind tunnel session", 250_000, category="Chassis & Aero")
        service.add("Driver salary", 1_000_000, category="Personnel")

        [expense] = service.list(category="Personnel")
        assert expense.description == "Driver salary"


class TestSummary:
    def test_totals_everything_with_no_month(self, service):
        service.add("Wind tunnel session", 250_000)
        service.add("Driver salary", 1_000_000)

        assert service.summary() == 1_250_000

    def test_scopes_total_to_a_month(self, service, fake_repository):
        this_month = date.today().replace(day=1)
        fake_repository.insert("Wind tunnel session", 250_000, "General", this_month)

        assert service.summary(month=this_month.month) == 250_000

    @pytest.mark.parametrize("month", [0, 13, -1])
    def test_rejects_out_of_range_month(self, service, month):
        with pytest.raises(InvalidMonthError):
            service.summary(month=month)


class TestSetBudget:
    def test_sets_a_cap_for_a_month(self, service, fake_repository):
        service.set_budget(3, 500_000)

        assert fake_repository.get_budget(3) == 500_000

    @pytest.mark.parametrize("month", [0, 13])
    def test_rejects_invalid_month(self, service, month):
        with pytest.raises(InvalidMonthError):
            service.set_budget(month, 500_000)

    def test_rejects_non_positive_cap(self, service):
        with pytest.raises(InvalidCapError):
            service.set_budget(3, 0)


class TestExportCsv:
    def test_writes_header_and_rows_and_returns_the_count(self, service, tmp_path):
        service.add("Wind tunnel session", 250_000, category="Chassis & Aero")
        output_path = tmp_path / "expenses.csv"

        count = service.export_csv(str(output_path))

        assert count == 1
        lines = output_path.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "id,date,category,description,amount"
        assert lines[1].endswith("Chassis & Aero,Wind tunnel session,250000.00")

    def test_raises_export_error_on_unwritable_path(self, service, tmp_path):
        service.add("Wind tunnel session", 250_000)
        unwritable_path = tmp_path / "missing-dir" / "expenses.csv"

        with pytest.raises(ExportError):
            service.export_csv(str(unwritable_path))
