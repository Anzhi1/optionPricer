from dataclasses import dataclass
from datetime import date
from math import isfinite

from option_pricer.termstructures.yield_curve import YieldTermStructure, forward_rate
from option_pricer.time.daycounters import DayCounter


@dataclass(frozen=True)
class FloatingRateCoupon:
    """Floating-rate coupon projected from a discount curve."""

    accrual_start: date
    accrual_end: date
    payment_date: date
    notional: float
    spread: float
    day_count: DayCounter
    projection_curve: YieldTermStructure

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
        if not isfinite(self.spread):
            raise ValueError("spread must be finite")

    def rate(self) -> float:
        return forward_rate(
            self.projection_curve,
            self.accrual_start,
            self.accrual_end,
            self.day_count,
        ) + self.spread

    def amount(self) -> float:
        accrual = self.day_count.year_fraction(self.accrual_start, self.accrual_end)
        return self.notional * self.rate() * accrual
