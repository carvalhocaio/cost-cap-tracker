"""Tests for SqliteRepository against a real (tmp_path-backed) SQLite
database -- the one layer allowed to touch actual SQL."""

from datetime import date

import pytest

from cost_cap_tracker.errors import CorruptDataError, NotFoundError
from cost_cap_tracker.infrastructure.sqlite_repository import SqliteRepository


@pytest.fixture
def repo(tmp_path):
    repository = SqliteRepository(str(tmp_path / "test.db"))
    yield repository
    repository.close()


class TestInsert:
    def test_returns_an_incrementing_id(self, repo):
        first_id = repo.insert("Wind tunnel session", 250_000, "General", date.today())
        second_id = repo.insert("Driver salary", 1_000_000, "General", date.today())

        assert second_id == first_id + 1

    def test_row_is_retrievable_via_list(self, repo):
        repo.insert("Wind tunnel session", 250_000, "Chassis & Aero", date.today())

        [expense] = repo.list()
        assert expense.description == "Wind tunnel session"
        assert expense.amount == 250_000
        assert expense.category == "Chassis & Aero"


class TestUpdate:
    def test_updates_only_given_fields(self, repo):
        expense_id = repo.insert(
            "Wind tunnel session", 250_000, "General", date.today()
        )

        repo.update(expense_id, description=None, amount=260_000, category=None)

        [expense] = repo.list()
        assert expense.amount == 260_000
        assert expense.description == "Wind tunnel session"

    def test_raises_not_found_for_missing_id(self, repo):
        with pytest.raises(NotFoundError):
            repo.update(99, description="x", amount=None, category=None)


class TestDelete:
    def test_removes_the_row(self, repo):
        expense_id = repo.insert(
            "Wind tunnel session", 250_000, "General", date.today()
        )

        repo.delete(expense_id)

        assert repo.list() == []

    def test_raises_not_found_for_missing_id(self, repo):
        with pytest.raises(NotFoundError):
            repo.delete(99)


class TestList:
    def test_orders_newest_first(self, repo):
        repo.insert("Older", 1, "General", date(2026, 1, 1))
        repo.insert("Newer", 1, "General", date(2026, 3, 1))

        expenses = repo.list()
        assert [expense.description for expense in expenses] == ["Newer", "Older"]

    def test_filters_by_category_case_insensitively(self, repo):
        repo.insert("Wind tunnel session", 1, "Chassis & Aero", date.today())
        repo.insert("Driver salary", 1, "Personnel", date.today())

        [expense] = repo.list(category="personnel")
        assert expense.description == "Driver salary"

    def test_returns_empty_list_when_no_expenses(self, repo):
        assert repo.list() == []


class TestTotal:
    def test_sums_everything_with_no_month(self, repo):
        repo.insert("A", 100, "General", date.today())
        repo.insert("B", 200, "General", date.today())

        assert repo.total() == 300

    def test_scopes_to_a_month_of_the_current_year(self, repo):
        today = date.today()
        repo.insert("This month", 100, "General", today)

        assert repo.total(month=today.month) == 100

    def test_excludes_same_month_from_a_different_year(self, repo):
        today = date.today()
        repo.insert("This month, this year", 100, "General", today)
        other_year_date = f"{today.year - 1}-{today.month:02d}-01"
        repo._conn.execute(
            "INSERT INTO expenses (description, amount, category, date) "
            "VALUES (?, ?, ?, ?)",
            ("This month, last year", 100, "General", other_year_date),
        )
        repo._conn.commit()

        assert repo.total(month=today.month) == 100

    def test_returns_zero_when_nothing_matches(self, repo):
        assert repo.total(month=1) == 0


class TestBudget:
    def test_round_trips(self, repo):
        repo.set_budget(3, 500_000)

        assert repo.get_budget(3) == 500_000

    def test_overwrites_existing_cap_for_the_same_month(self, repo):
        repo.set_budget(3, 500_000)
        repo.set_budget(3, 600_000)

        assert repo.get_budget(3) == 600_000

    def test_returns_none_when_unset(self, repo):
        assert repo.get_budget(3) is None


class TestSchema:
    def test_opening_the_same_file_twice_does_not_error(self, tmp_path):
        path = str(tmp_path / "shared.db")
        first = SqliteRepository(path)
        second = SqliteRepository(path)

        first.close()
        second.close()


class TestCorruptData:
    def test_raises_corrupt_data_error_on_unparseable_date(self, repo):
        repo._conn.execute(
            "INSERT INTO expenses (description, amount, category, date) "
            "VALUES (?, ?, ?, ?)",
            ("Bad row", 100, "General", "not-a-date"),
        )
        repo._conn.commit()

        with pytest.raises(CorruptDataError):
            repo.list()
