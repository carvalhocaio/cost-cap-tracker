use chrono::NaiveDate;

// Default category applied when the user doesn't pass `--category`.
pub const DEFAULT_CATEGORY: &str = "General";

/// Categories that mirror how an F1 team's spending is actually broken
/// down under the FIA cost cap (power unit is capped separately, chassis
/// & aero is where most development budget goes, etc). Purely a set of
/// suggestions surfaced in `--help` -- the field itself is a free string,
/// so nothing stops you from adding your own.
pub const SUGGESTED_CATEGORIES: [&str; 6] = [
    "Power Unit",
    "Chassis & Aero",
    "Personnel",
    "Logistics",
    "CapEx",
    "General",
];

#[derive(Debug, Clone, PartialEq)]
pub struct Expense {
    pub id: i64,
    pub description: String,
    pub amount: f64,
    pub category: String,
    pub date: NaiveDate,
}
