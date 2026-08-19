use cost_cap_tracker::errors::AppError;
use cost_cap_tracker::service::ExpenseService;
use cost_cap_tracker::storage::SqliteRepository;

fn service() -> ExpenseService<SqliteRepository> {
    let repo = SqliteRepository::open(":memory:").expect("open in-memory db");
    ExpenseService::new(repo)
}

#[test]
fn add_and_list_round_trips() {
    let svc = service();
    svc.add("Lunch", 20.0, None).unwrap();
    svc.add("Dinner", 10.0, Some("Personnel")).unwrap();

    let expenses = svc.list(None).unwrap();
    assert_eq!(expenses.len(), 2);
    assert_eq!(
        expenses
            .iter()
            .find(|e| e.description == "Lunch")
            .unwrap()
            .category,
        "General"
    );
    assert_eq!(
        expenses
            .iter()
            .find(|e| e.description == "Dinner")
            .unwrap()
            .category,
        "Personnel"
    );
}

#[test]
fn rejects_non_positive_amount() {
    let svc = service();
    let err = svc.add("Bad expense", 0.0, None).unwrap_err();
    assert!(matches!(err, AppError::InvalidAmount));

    let err = svc.add("Also bad", -5.0, None).unwrap_err();
    assert!(matches!(err, AppError::InvalidAmount));
}

#[test]
fn delete_removes_expense_and_errors_on_missing_id() {
    let svc = service();
    let outcome = svc.add("Lunch", 20.0, None).unwrap();

    svc.delete(outcome.id).unwrap();
    assert_eq!(svc.list(None).unwrap().len(), 0);

    let err = svc.delete(outcome.id).unwrap_err();
    assert!(matches!(err, AppError::NotFound(_)));
}

#[test]
fn update_changes_only_the_given_fields() {
    let svc = service();
    let outcome = svc.add("Lunch", 20.0, None).unwrap();

    svc.update(outcome.id, None, Some(25.0), None).unwrap();

    let expense = svc.list(None).unwrap().into_iter().next().unwrap();
    assert_eq!(expense.description, "Lunch");
    assert_eq!(expense.amount, 25.0);
}

#[test]
fn update_with_no_fields_is_rejected() {
    let svc = service();
    let outcome = svc.add("Lunch", 20.0, None).unwrap();

    let err = svc.update(outcome.id, None, None, None).unwrap_err();
    assert!(matches!(err, AppError::EmptyUpdate));
}

#[test]
fn list_filters_by_category() {
    let svc = service();
    svc.add("Engine rebuild", 500.0, Some("Power Unit"))
        .unwrap();
    svc.add("Flight tickets", 200.0, Some("Logistics")).unwrap();

    let power_unit = svc.list(Some("Power Unit")).unwrap();
    assert_eq!(power_unit.len(), 1);
    assert_eq!(power_unit[0].description, "Engine rebuild");
}

#[test]
fn summary_totals_everything_without_a_month_filter() {
    let svc = service();
    svc.add("Lunch", 20.0, None).unwrap();
    svc.add("Dinner", 10.0, None).unwrap();

    assert_eq!(svc.summary(None).unwrap(), 30.0);
}

#[test]
fn summary_rejects_invalid_month() {
    let svc = service();
    let err = svc.summary(Some(13)).unwrap_err();
    assert!(matches!(err, AppError::InvalidMonth));
}

#[test]
fn budget_status_flags_a_breach() {
    use chrono::{Datelike, Local};

    let svc = service();
    let month = Local::now().date_naive().month();
    svc.set_budget(month, 15.0).unwrap();

    let outcome = svc.add("Big expense", 20.0, None).unwrap();
    let status = outcome
        .budget_status
        .expect("budget was set for this month");

    assert!(status.is_breach());
    assert_eq!(status.total, 20.0);
    assert_eq!(status.cap, 15.0);
}

#[test]
fn no_budget_status_when_no_budget_set() {
    let svc = service();
    let outcome = svc.add("Lunch", 20.0, None).unwrap();
    assert!(outcome.budget_status.is_none());
}
