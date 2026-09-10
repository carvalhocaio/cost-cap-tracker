"""Tests for the centralized AppError hierarchy."""

import pytest

from cost_cap_tracker.errors import (
    AppError,
    CorruptDataError,
    EmptyUpdateError,
    ExportError,
    InvalidAmountError,
    InvalidCapError,
    InvalidMonthError,
    NotFoundError,
    StorageError,
)


class TestNotFoundError:
    def test_message_includes_the_expense_id(self):
        error = NotFoundError(5)

        assert str(error) == "expense with id 5 not found"
        assert error.expense_id == 5
        assert isinstance(error, AppError)


class TestFixedMessageErrors:
    @pytest.mark.parametrize(
        ("error_type", "message"),
        [
            (InvalidAmountError, "amount must be greater than zero"),
            (InvalidMonthError, "month must be between 1 and 12"),
            (InvalidCapError, "cost cap must be greater than zero"),
            (
                EmptyUpdateError,
                "update must change at least one field "
                "(description, amount or category)",
            ),
        ],
    )
    def test_has_expected_message(self, error_type, message):
        error = error_type()

        assert str(error) == message
        assert isinstance(error, AppError)


class TestWrappedCauseErrors:
    @pytest.mark.parametrize(
        ("error_type", "prefix"),
        [
            (StorageError, "database error:"),
            (ExportError, "export error:"),
            (CorruptDataError, "corrupt data:"),
        ],
    )
    def test_message_includes_the_wrapped_cause(self, error_type, prefix):
        cause = ValueError("boom")

        error = error_type(cause)

        assert str(error) == f"{prefix} {cause}"
        assert error.cause is cause
        assert isinstance(error, AppError)
