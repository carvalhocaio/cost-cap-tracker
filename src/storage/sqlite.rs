use chrono::{Datelike, Local, NaiveDate};
use rusqlite::{params, Connection, OptionalExtension};

use super::ExpenseRepository;
use crate::domain::Expense;
use crate::errors::{AppError, AppResult};

pub struct SqliteRepository {
    conn: Connection,
}

impl SqliteRepository {
    /// Opens (or creates) the database file at `path` and applies the
    /// schema. `:memory:` works too, which is what the integration tests
    /// use to stay hermetic.
    pub fn open(path: &str) -> AppResult<Self> {
        let conn = Connection::open(path)?;
        conn.execute_batch(
            "
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
            ",
        )?;
        Ok(Self { conn })
    }

    fn row_to_expense(row: &rusqlite::Row) -> rusqlite::Result<Expense> {
        let date_str: String = row.get("date")?;
        let date = NaiveDate::parse_from_str(&date_str, "%Y-%m-%d")
            .unwrap_or_else(|_| Local::now().date_naive());
        Ok(Expense {
            id: row.get("id")?,
            description: row.get("description")?,
            amount: row.get("amount")?,
            category: row.get("category")?,
            date,
        })
    }
}

impl ExpenseRepository for SqliteRepository {
    fn insert(
        &self,
        description: &str,
        amount: f64,
        category: &str,
        date: NaiveDate,
    ) -> AppResult<i64> {
        self.conn.execute(
            "INSERT INTO expenses (description, amount, category, date) VALUES (?1, ?2, ?3, ?4)",
            params![
                description,
                amount,
                category,
                date.format("%Y-%m-%d").to_string()
            ],
        )?;
        Ok(self.conn.last_insert_rowid())
    }

    fn update(
        &self,
        id: i64,
        description: Option<&str>,
        amount: Option<f64>,
        category: Option<&str>,
    ) -> AppResult<()> {
        let affected = self.conn.execute(
            "UPDATE expenses SET
                description = COALESCE(?1, description),
                amount      = COALESCE(?2, amount),
                category    = COALESCE(?3, category)
             WHERE id = ?4",
            params![description, amount, category, id],
        )?;
        if affected == 0 {
            return Err(AppError::NotFound(id));
        }
        Ok(())
    }

    fn delete(&self, id: i64) -> AppResult<()> {
        let affected = self
            .conn
            .execute("DELETE FROM expenses WHERE id = ?1", params![id])?;
        if affected == 0 {
            return Err(AppError::NotFound(id));
        }
        Ok(())
    }

    fn list(&self, category: Option<&str>) -> AppResult<Vec<Expense>> {
        let mut stmt = match category {
            Some(_) => self.conn.prepare(
                "SELECT id, description, amount, category, date FROM expenses
                 WHERE category = ?1 COLLATE NOCASE ORDER BY date DESC, id DESC",
            )?,
            None => self.conn.prepare(
                "SELECT id, description, amount, category, date FROM expenses
                 ORDER BY date DESC, id DESC",
            )?,
        };

        let rows = match category {
            Some(cat) => stmt.query_map(params![cat], Self::row_to_expense)?,
            None => stmt.query_map(params![], Self::row_to_expense)?,
        };

        rows.collect::<rusqlite::Result<Vec<_>>>()
            .map_err(AppError::from)
    }

    fn total(&self, month: Option<u32>) -> AppResult<f64> {
        let total: f64 = match month {
            Some(m) => {
                let year = Local::now().year();
                let month_str = format!("{:02}", m);
                let year_str = year.to_string();
                self.conn.query_row(
                    "SELECT COALESCE(SUM(amount), 0.0) FROM expenses
                     WHERE strftime('%m', date) = ?1 AND strftime('%Y', date) = ?2",
                    params![month_str, year_str],
                    |row| row.get(0),
                )?
            }
            None => self.conn.query_row(
                "SELECT COALESCE(SUM(amount), 0.0) FROM expenses",
                [],
                |row| row.get(0),
            )?,
        };
        Ok(total)
    }

    fn set_budget(&self, month: u32, cap: f64) -> AppResult<()> {
        self.conn.execute(
            "INSERT INTO budgets (month, cap) VALUES (?1, ?2)
             ON CONFLICT(month) DO UPDATE SET cap = excluded.cap",
            params![month, cap],
        )?;
        Ok(())
    }

    fn get_budget(&self, month: u32) -> AppResult<Option<f64>> {
        self.conn
            .query_row(
                "SELECT cap FROM budgets WHERE month = ?1",
                params![month],
                |row| row.get(0),
            )
            .optional()
            .map_err(AppError::from)
    }
}
