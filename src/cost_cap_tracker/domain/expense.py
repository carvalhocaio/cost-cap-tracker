"""Pure expense model and category vocabulary -- no I/O, no persistence."""

from dataclasses import dataclass
from datetime import date

DEFAULT_CATEGORY = "General"

SUGGESTED_CATEGORIES: tuple[str, ...] = (
    "Power Unit",
    "Chassis & Aero",
    "Personnel",
    "Logistics",
    "CapEx",
    "General",
)


@dataclass(frozen=True, slots=True)
class Expense:
    id: int
    description: str
    amount: float
    category: str
    date: date
