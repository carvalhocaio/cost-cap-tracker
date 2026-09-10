"""Tests for the argparse CLI surface."""

import pytest

from cost_cap_tracker.infrastructure.cli.parser import build_parser


@pytest.fixture
def parser():
    return build_parser()


class TestAdd:
    def test_parses_required_and_optional_flags(self, parser):
        args = parser.parse_args(
            ["add", "--description", "Wind tunnel", "--amount", "250000"]
        )

        assert args.command == "add"
        assert args.description == "Wind tunnel"
        assert args.amount == 250000.0
        assert args.category is None

    def test_accepts_a_category(self, parser):
        args = parser.parse_args(
            ["add", "--description", "x", "--amount", "1", "--category", "Personnel"]
        )

        assert args.category == "Personnel"

    def test_missing_required_flag_raises_system_exit(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["add", "--amount", "1"])


class TestUpdate:
    def test_parses_partial_fields(self, parser):
        args = parser.parse_args(["update", "--id", "1", "--amount", "260000"])

        assert args.id == 1
        assert args.amount == 260000.0
        assert args.description is None
        assert args.category is None


class TestDelete:
    def test_parses_id(self, parser):
        args = parser.parse_args(["delete", "--id", "1"])

        assert args.id == 1


class TestList:
    def test_defaults_category_to_none(self, parser):
        args = parser.parse_args(["list"])

        assert args.category is None

    def test_accepts_a_category_filter(self, parser):
        args = parser.parse_args(["list", "--category", "Personnel"])

        assert args.category == "Personnel"


class TestSummary:
    def test_defaults_month_to_none(self, parser):
        args = parser.parse_args(["summary"])

        assert args.month is None

    def test_accepts_a_month(self, parser):
        args = parser.parse_args(["summary", "--month", "3"])

        assert args.month == 3


class TestSetBudget:
    def test_parses_month_and_cap(self, parser):
        args = parser.parse_args(["set-budget", "--month", "3", "--cap", "500000"])

        assert args.month == 3
        assert args.cap == 500000.0

    def test_accepts_negative_cap(self, parser):
        args = parser.parse_args(["set-budget", "--month", "3", "--cap", "-1"])

        assert args.cap == -1.0


class TestExport:
    def test_defaults_output_filename(self, parser):
        args = parser.parse_args(["export"])

        assert args.output == "expenses.csv"

    def test_accepts_a_custom_output_path(self, parser):
        args = parser.parse_args(["export", "--output", "out.csv"])

        assert args.output == "out.csv"


class TestCategories:
    def test_parses_with_no_extra_flags(self, parser):
        args = parser.parse_args(["categories"])

        assert args.command == "categories"


class TestNegativeNumbers:
    def test_amount_accepts_a_negative_value(self, parser):
        args = parser.parse_args(["add", "--description", "x", "--amount", "-5.0"])

        assert args.amount == -5.0


class TestUnknownCommand:
    def test_raises_system_exit(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args(["frobnicate"])
