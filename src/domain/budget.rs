/// Result of checking a month's total spend against its cost cap, if one
/// was ever set with `set-budget`. Named after the FIA's own vocabulary:
/// a team that goes over isn't "over budget", it's in *breach* of the cap.
#[derive(Debug, Clone, PartialEq)]
pub struct BudgetStatus {
    pub month: u32,
    pub total: f64,
    pub cap: f64,
}

impl BudgetStatus {
    pub fn is_breach(&self) -> bool {
        self.total > self.cap
    }

    pub fn remaining(&self) -> f64 {
        self.cap - self.total
    }
}
