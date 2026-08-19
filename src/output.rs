use crate::domain::{BudgetStatus, Expense};

pub fn print_add_success(id: i64) {
    println!("Expense added successfully (ID: {id})");
}

pub fn print_expenses(expenses: &[Expense]) {
    if expenses.is_empty() {
        println!("No expenses yet.");
        return;
    }

    let id_w = expenses
        .iter()
        .map(|e| e.id.to_string().len())
        .max()
        .unwrap_or(2)
        .max(2);
    let cat_w = expenses
        .iter()
        .map(|e| e.category.len())
        .max()
        .unwrap_or(8)
        .max(8);
    let desc_w = expenses
        .iter()
        .map(|e| e.description.len())
        .max()
        .unwrap_or(11)
        .max(11);

    println!(
        "{:<id_w$}  {:<10}  {:<cat_w$}  {:<desc_w$}  Amount",
        "ID", "Date", "Category", "Description"
    );
    for e in expenses {
        println!(
            "{:<id_w$}  {:<10}  {:<cat_w$}  {:<desc_w$}  ${:.2}",
            e.id,
            e.date.format("%Y-%m-%d"),
            e.category,
            e.description,
            e.amount
        );
    }
}

/// Prints either a calm "here's where you stand" line or, if the month's
/// spend has gone past its cap, a breach warning -- echoing the language
/// the FIA itself uses when a team overspends the cost cap.
pub fn print_budget_status(status: &BudgetStatus) {
    if status.is_breach() {
        println!(
            "\n🚩 Cost Cap breach for month {:02}: spent ${:.2} against a ${:.2} cap (${:.2} over).",
            status.month,
            status.total,
            status.cap,
            status.total - status.cap
        );
    } else {
        println!(
            "   (month {:02} cost cap: ${:.2} of ${:.2} used, ${:.2} remaining)",
            status.month,
            status.total,
            status.cap,
            status.remaining()
        );
    }
}
