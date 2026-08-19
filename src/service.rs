use chrono::{Datelike, Local};

use crate::domain::{BudgetStatus, Expense, DEFAULT_CATEGORY};
use crate::errors::{AppError, AppResult};
use crate::storage::ExpenseRepository;

/// What `add()` hands back: the new id, plus how that expense's month
/// looks against its cost cap, if one has been set.
#[derive(Debug)]
pub struct AddOutcome {
    pub id: i64,
    pub budget_status: Option<BudgetStatus>,
}

pub struct ExpenseService<R: ExpenseRepository> {
    repo: R,
}

impl<R: ExpenseRepository> ExpenseService<R> {
    pub fn new(repo: R) -> Self {
        Self { repo }
    }

    pub fn add(
        &self,
        description: &str,
        amount: f64,
        category: Option<&str>,
    ) -> AppResult<AddOutcome> {
        if amount <= 0.0 {
            return Err(AppError::InvalidAmount);
        }
        let category = category.unwrap_or(DEFAULT_CATEGORY);
        let today = Local::now().date_naive();
        let id = self.repo.insert(description, amount, category, today)?;

        let month = today.month();
        let budget_status = match self.repo.get_budget(month)? {
            Some(cap) => {
                let total = self.repo.total(Some(month))?;
                Some(BudgetStatus { month, total, cap })
            }
            None => None,
        };

        Ok(AddOutcome { id, budget_status })
    }

    pub fn update(
        &self,
        id: i64,
        description: Option<&str>,
        amount: Option<f64>,
        category: Option<&str>,
    ) -> AppResult<()> {
        if description.is_none() && amount.is_none() && category.is_none() {
            return Err(AppError::EmptyUpdate);
        }
        if let Some(a) = amount {
            if a <= 0.0 {
                return Err(AppError::InvalidAmount);
            }
        }
        self.repo.update(id, description, amount, category)
    }

    pub fn delete(&self, id: i64) -> AppResult<()> {
        self.repo.delete(id)
    }

    pub fn list(&self, category: Option<&str>) -> AppResult<Vec<Expense>> {
        self.repo.list(category)
    }

    /// Total spend, optionally scoped to `month` of the current year.
    pub fn summary(&self, month: Option<u32>) -> AppResult<f64> {
        if let Some(m) = month {
            if !(1..=12).contains(&m) {
                return Err(AppError::InvalidMonth);
            }
        }
        self.repo.total(month)
    }

    pub fn set_budget(&self, month: u32, cap: f64) -> AppResult<()> {
        if !(1..=12).contains(&month) {
            return Err(AppError::InvalidMonth);
        }
        if cap <= 0.0 {
            return Err(AppError::InvalidCap);
        }
        self.repo.set_budget(month, cap)
    }

    /// Exports every expense to a CSV file and returns how many rows were written.
    pub fn export_csv(&self, path: &str) -> AppResult<usize> {
        let expenses = self.repo.list(None)?;
        let mut writer = csv::Writer::from_path(path)?;
        writer.write_record(["id", "date", "category", "description", "amount"])?;
        for e in &expenses {
            writer.write_record([
                e.id.to_string(),
                e.date.format("%Y-%m-%d").to_string(),
                e.category.clone(),
                e.description.clone(),
                format!("{:.2}", e.amount),
            ])?;
        }
        writer.flush()?;
        Ok(expenses.len())
    }
}
