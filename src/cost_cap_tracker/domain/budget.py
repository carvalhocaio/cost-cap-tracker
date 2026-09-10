"""Result of checking a month's total spend against its cost cap, if one
was set with `set-budget`. A team that goes over isn't "over budget",
it's in breach of the cap -- FIA vocabulary, kept from the Rust version.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BudgetStatus:
    month: int
    total: float
    cap: float

    def is_breach(self) -> bool:
        return self.total > self.cap

    def remaining(self) -> float:
        return self.cap - self.total
