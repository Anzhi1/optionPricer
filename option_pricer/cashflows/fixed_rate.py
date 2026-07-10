from dataclasses import dataclass
from datetime import date
from math import isfinite

from option_pricer.time.daycounters import DayCounter


@dataclass(frozen=True)
class FixedRateCoupon:
    """Fixed-rate coupon over an accrual period."""

    accrual_start: date
    accrual_end: date
    payment_date: date
    notional: float
    fixed_rate: float
    day_count: DayCounter

    def __post_init__(self) -> None:
        if not isinstance(self.accrual_start, date):
            raise TypeError("accrual_start must be a date")
        if not isinstance(self.accrual_end, date):
            raise TypeError("accrual_end must be a date")
        if not isinstance(self.payment_date, date):
            raise TypeError("payment_date must be a date")
        if self.accrual_end <= self.accrual_start:
            raise ValueError("accrual_end must be after accrual_start")
        if not isfinite(self.notional):
            raise ValueError("notional must be finite")
        if self.notional <= 0.0:
            raise ValueError("notional must be positive")
        if not isfinite(self.fixed_rate):
            raise ValueError("fixed_rate must be finite")

    def amount(self) -> float:
        accrual = self.day_count.year_fraction(self.accrual_start, self.accrual_end)
        return self.notional * self.fixed_rate * accrual
