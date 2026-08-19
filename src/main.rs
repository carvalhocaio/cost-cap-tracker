use clap::Parser;
use cost_cap_tracker::cli::{Cli, Commands};
use cost_cap_tracker::errors::AppResult;
use cost_cap_tracker::service::ExpenseService;
use cost_cap_tracker::storage::{ExpenseRepository, SqliteRepository};
use cost_cap_tracker::{domain, output};

/// Filename is a small nod to Twenty One Pilots' debut album -- a vessel
/// being, quite literally, a container for something you carry with you.
const DB_PATH: &str = "vessel.db";

const MONTH_NAMES: [&str; 12] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

fn main() {
    let cli = Cli::parse();

    let repo = match SqliteRepository::open(DB_PATH) {
        Ok(repo) => repo,
        Err(e) => {
            eprintln!("Error: {e}");
            std::process::exit(1);
        }
    };
    let service = ExpenseService::new(repo);

    if let Err(e) = run(&service, cli.command) {
        eprintln!("Error: {e}");
        std::process::exit(1);
    }
}

fn run<R: ExpenseRepository>(service: &ExpenseService<R>, command: Commands) -> AppResult<()> {
    match command {
        Commands::Add {
            description,
            amount,
            category,
        } => {
            let outcome = service.add(&description, amount, category.as_deref())?;
            output::print_add_success(outcome.id);
            if let Some(status) = outcome.budget_status {
                output::print_budget_status(&status);
            }
        }

        Commands::Update {
            id,
            description,
            amount,
            category,
        } => {
            service.update(id, description.as_deref(), amount, category.as_deref())?;
            println!("Expense updated successfully");
        }

        Commands::Delete { id } => {
            service.delete(id)?;
            println!("Expense deleted successfully");
        }

        Commands::List { category } => {
            let expenses = service.list(category.as_deref())?;
            output::print_expenses(&expenses);
        }

        Commands::Summary { month } => {
            let total = service.summary(month)?;
            match month {
                Some(m) => {
                    let month_name = MONTH_NAMES[(m - 1) as usize];
                    println!("Total expenses for {month_name}: ${total:.2}");
                }
                None => println!("Total expenses: ${total:.2}"),
            }
        }

        Commands::SetBudget { month, cap } => {
            service.set_budget(month, cap)?;
            let month_name = MONTH_NAMES[(month - 1) as usize];
            println!("Cost cap for {month_name} set to ${cap:.2}");
        }

        Commands::Export { output: path } => {
            let count = service.export_csv(&path)?;
            println!("Exported {count} expense(s) to {path}");
        }

        Commands::Categories => {
            println!("Suggested categories:");
            for category in domain::SUGGESTED_CATEGORIES {
                println!("  - {category}");
            }
        }
    }
    Ok(())
}
