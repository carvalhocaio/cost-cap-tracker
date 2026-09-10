"""Tests for BudgetStatus, the result of checking a month's spend against
its cost cap."""

from cost_cap_tracker.domain.budget import BudgetStatus


class TestIsBreach:
    def test_true_when_total_exceeds_cap(self):
        status = BudgetStatus(month=3, total=600_000, cap=500_000)

        assert status.is_breach() is True

    def test_false_when_total_equals_cap(self):
        status = BudgetStatus(month=3, total=500_000, cap=500_000)

        assert status.is_breach() is False

    def test_false_when_total_is_under_cap(self):
        status = BudgetStatus(month=3, total=400_000, cap=500_000)

        assert status.is_breach() is False


class TestRemaining:
    def test_positive_when_under_cap(self):
        status = BudgetStatus(month=3, total=400_000, cap=500_000)

        assert status.remaining() == 100_000

    def test_negative_when_over_cap(self):
        status = BudgetStatus(month=3, total=600_000, cap=500_000)

        assert status.remaining() == -100_000
