"""Tests for the Expense domain model and category vocabulary."""

import dataclasses
from datetime import date

import pytest

from cost_cap_tracker.domain.expense import (
    DEFAULT_CATEGORY,
    SUGGESTED_CATEGORIES,
    Expense,
)


class TestDefaultCategory:
    def test_default_category_is_general(self):
        assert DEFAULT_CATEGORY == "General"


class TestSuggestedCategories:
    def test_lists_the_six_f1_themed_categories_in_order(self):
        assert SUGGESTED_CATEGORIES == (
            "Power Unit",
            "Chassis & Aero",
            "Personnel",
            "Logistics",
            "CapEx",
            "General",
        )


class TestExpense:
    def test_expenses_with_equal_fields_compare_equal(self):
        first = Expense(
            id=1,
            description="Wind tunnel session",
            amount=250_000,
            category="Chassis & Aero",
            date=date(2026, 3, 1),
        )
        second = Expense(
            id=1,
            description="Wind tunnel session",
            amount=250_000,
            category="Chassis & Aero",
            date=date(2026, 3, 1),
        )

        assert first == second

    def test_is_immutable(self):
        expense = Expense(
            id=1,
            description="Wind tunnel session",
            amount=250_000,
            category="Chassis & Aero",
            date=date(2026, 3, 1),
        )

        with pytest.raises(dataclasses.FrozenInstanceError):
            expense.amount = 300_000
