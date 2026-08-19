use thiserror::Error;

/// A single error type for the whole application. Keeping this centralized
/// means every layer (storage, service, cli) can bundle errors up with `?`
/// and main.rs has one place to decide how to print them and what exit
/// code to use.
#[derive(Debug, Error)]
pub enum AppError {
    #[error("expense with id {0} not found")]
    NotFound(i64),

    #[error("amount must be greater than zero")]
    InvalidAmount,

    #[error("month must be between 1 and 12")]
    InvalidMonth,

    #[error("cost cap must be greater than zero")]
    InvalidCap,

    #[error("update must change at least one field (description, amount or category)")]
    EmptyUpdate,

    #[error("database error: {0}")]
    Db(#[from] rusqlite::Error),

    #[error("csv error: {0}")]
    Csv(#[from] csv::Error),

    #[error("io error: {0}")]
    IO(#[from] std::io::Error),
}

pub type AppResult<T> = Result<T, AppError>;
