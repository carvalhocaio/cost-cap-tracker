"""SQLite adapter for ExpenseRepository. Uses stdlib sqlite3 only -- no
new dependency, matching the Rust version's relational model (`expenses`
and `budgets` tables with the same CHECK constraints)."""

from __future__ import annotations

import sqlite3
from datetime import date

from cost_cap_tracker.domain.expense import Expense
from cost_cap_tracker.errors import CorruptDataError, NotFoundError, StorageError

_SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT    NOT NULL,
    amount      REAL    NOT NULL CHECK (amount > 0),
    category    TEXT    NOT NULL,
    date        TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    month INTEGER PRIMARY KEY CHECK (month BETWEEN 1 AND 12),
    cap   REAL    NOT NULL CHECK (cap > 0)
);
"""


class SqliteRepository:
    def __init__(self, path: str) -> None:
        self._conn = sqlite3.connect(path)
        try:
            with self._conn:
                self._conn.executescript(_SCHEMA)
        except sqlite3.Error as error:
            raise StorageError(error) from error

    def close(self) -> None:
        self._conn.close()

    def insert(
        self, description: str, amount: float, category: str, expense_date: date
    ) -> int:
        cursor = self._execute(
            "INSERT INTO expenses (description, amount, category, date) "
            "VALUES (?, ?, ?, ?)",
            (description, amount, category, expense_date.isoformat()),
        )
        return cursor.lastrowid

    def update(
        self,
        expense_id: int,
        description: str | None,
        amount: float | None,
        category: str | None,
    ) -> None:
        fields = []
        params: list[object] = []
        if description is not None:
            fields.append("description = ?")
            params.append(description)
        if amount is not None:
            fields.append("amount = ?")
            params.append(amount)
        if category is not None:
            fields.append("category = ?")
            params.append(category)
        params.append(expense_id)

        cursor = self._execute(
            f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?", tuple(params)
        )
        if cursor.rowcount == 0:
            raise NotFoundError(expense_id)

    def delete(self, expense_id: int) -> None:
        cursor = self._execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(expense_id)

    def list(self, category: str | None = None) -> list[Expense]:
        sql = "SELECT id, description, amount, category, date FROM expenses"
        params: tuple[object, ...] = ()
        if category is not None:
            sql += " WHERE category = ? COLLATE NOCASE"
            params = (category,)
        sql += " ORDER BY date DESC, id DESC"

        rows = self._query(sql, params)
        return [self._row_to_expense(row) for row in rows]

    def total(self, month: int | None = None) -> float:
        sql = "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        params: tuple[object, ...] = ()
        if month is not None:
            sql += " WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?"
            params = (f"{month:02d}", str(date.today().year))

        rows = self._query(sql, params)
        return rows[0][0]

    def set_budget(self, month: int, cap: float) -> None:
        self._execute(
            "INSERT INTO budgets (month, cap) VALUES (?, ?) "
            "ON CONFLICT(month) DO UPDATE SET cap = excluded.cap",
            (month, cap),
        )

    def get_budget(self, month: int) -> float | None:
        rows = self._query("SELECT cap FROM budgets WHERE month = ?", (month,))
        return rows[0][0] if rows else None

    def _row_to_expense(self, row: tuple) -> Expense:
        expense_id, description, amount, category, date_str = row
        try:
            expense_date = date.fromisoformat(date_str)
        except ValueError as error:
            raise CorruptDataError(error) from error
        return Expense(
            id=expense_id,
            description=description,
            amount=amount,
            category=category,
            date=expense_date,
        )

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        try:
            with self._conn:
                return self._conn.execute(sql, params)
        except sqlite3.Error as error:
            raise StorageError(error) from error

    def _query(self, sql: str, params: tuple = ()) -> list[tuple]:
        try:
            return self._conn.execute(sql, params).fetchall()
        except sqlite3.Error as error:
            raise StorageError(error) from error
