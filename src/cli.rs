use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "cost-cap",
    version,
    about = "Track your own spending the way an F1 team tracks its cost cap"
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Add a new expense
    Add {
        #[arg(long)]
        description: String,
        /// Must be positive -- negative values are rejected (not silently flipped)
        #[arg(long, allow_negative_numbers = true)]
        amount: f64,
        /// e.g. "Power Unit", "Chassis & Aero", "Personnel", "Logistics", "CapEx" (defaults to "General")
        #[arg(long)]
        category: Option<String>,
    },

    /// Update an existing expense (only the fields you pass are changed)
    Update {
        #[arg(long)]
        id: i64,
        #[arg(long)]
        description: Option<String>,
        #[arg(long, allow_negative_numbers = true)]
        amount: Option<f64>,
        #[arg(long)]
        category: Option<String>,
    },

    /// Delete an expense by id
    Delete {
        #[arg(long)]
        id: i64,
    },

    /// List all expenses, optionally filtered by category
    List {
        #[arg(long)]
        category: Option<String>,
    },

    /// Show total spend, optionally scoped to a month (1-12) of the current year
    Summary {
        #[arg(long)]
        month: Option<u32>,
    },

    /// Set (or update) the cost cap for a month (1-12) of the current year
    SetBudget {
        #[arg(long)]
        month: u32,
        #[arg(long, allow_negative_numbers = true)]
        cap: f64,
    },

    /// Export all expenses to a CSV file
    Export {
        #[arg(long, default_value = "expenses.csv")]
        output: String,
    },

    /// List the suggested F1-cost-cap-flavored categories
    Categories,
}
