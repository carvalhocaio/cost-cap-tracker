mod sqlite;

pub use sqlite::SqliteRepository;

use crate::domain::Expense;
use crate::errors::AppResult;
use chrono::NaiveDate;

/// Everything the service layer needs from persistence, and nothing more.
/// The service depends on this trait, not on SQLite directly -- swapping
/// the backend later (say, to Postgres for a shared "team" version) means
/// writing a new impl of this trait, with zero changes to business logic.
pub trait ExpenseRepository {
    fn insert(
        &self,
        description: &str,
        amount: f64,
        category: &str,
        date: NaiveDate,
    ) -> AppResult<i64>;

    fn update(
        &self,
        id: i64,
        description: Option<&str>,
        amount: Option<f64>,
        category: Option<&str>,
    ) -> AppResult<()>;

    fn delete(&self, id: i64) -> AppResult<()>;

    /// Lists expenses, optionally filtered by category, newest first.
    fn list(&self, category: Option<&str>) -> AppResult<Vec<Expense>>;

    // Sums expenses. When `month` is given, restricts to that month of
    // the *current* year (per the spec: "summary for a specific month
    // of current year").
    fn total(&self, month: Option<u32>) -> AppResult<f64>;

    fn set_budget(&self, month: u32, cap: f64) -> AppResult<()>;

    fn get_budget(&self, month: u32) -> AppResult<Option<f64>>;
}
