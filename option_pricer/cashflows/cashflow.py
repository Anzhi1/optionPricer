from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Protocol


class Cashflow(Protocol):
    """Dated cashflow with an amount."""

    payment_date: date

    def amount(self) -> float:
        ...


@dataclass(frozen=True)
class FixedCashflow:
    """Fixed dated cashflow."""

    payment_date: date
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.payment_date, date):
            raise TypeError("payment_date must be a date")
        if not isfinite(self.value):
            raise ValueError("value must be finite")

    def amount(self) -> float:
        return self.value
