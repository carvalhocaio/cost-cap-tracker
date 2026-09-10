"""Centralized application error hierarchy. Every layer (infrastructure,
application, cli) raises or wraps into one of these, so the CLI's
composition root has exactly one type to catch and one place to decide
exit codes -- mirroring the Rust AppError enum.
"""


class AppError(Exception):
    """Base for every error the application can raise."""


class NotFoundError(AppError):
    def __init__(self, expense_id: int) -> None:
        super().__init__(f"expense with id {expense_id} not found")
        self.expense_id = expense_id


class InvalidAmountError(AppError):
    def __init__(self) -> None:
        super().__init__("amount must be greater than zero")


class InvalidMonthError(AppError):
    def __init__(self) -> None:
        super().__init__("month must be between 1 and 12")


class InvalidCapError(AppError):
    def __init__(self) -> None:
        super().__init__("cost cap must be greater than zero")


class EmptyUpdateError(AppError):
    def __init__(self) -> None:
        super().__init__(
            "update must change at least one field (description, amount or category)"
        )


class StorageError(AppError):
    """Wraps an underlying sqlite3.Error -- equivalent of Rust's Db variant."""

    def __init__(self, cause: Exception) -> None:
        super().__init__(f"database error: {cause}")
        self.cause = cause


class ExportError(AppError):
    """Wraps an OSError/csv.Error during CSV export -- equivalent of
    Rust's combined Csv + IO variants (Python doesn't need two distinct
    wrapper types here since both only ever occur inside export_csv)."""

    def __init__(self, cause: Exception) -> None:
        super().__init__(f"export error: {cause}")
        self.cause = cause


class CorruptDataError(AppError):
    """Raised when a stored expense's date cannot be parsed. New in the
    Python port: the Rust version silently fell back to today's date on
    an unparseable date, which is the smell this rewrite intentionally
    fixes by surfacing an error instead."""

    def __init__(self, cause: Exception) -> None:
        super().__init__(f"corrupt data: {cause}")
        self.cause = cause
