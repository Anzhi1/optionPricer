from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, log
from typing import Protocol

from option_pricer.math.interpolation import linear_interpolate
from option_pricer.termstructures.base import time_from_maturity, validate_date_configuration
from option_pricer.time.daycounters import DayCounter


class YieldTermStructure(Protocol):
    """Discount and zero-rate term structure."""

    def discount(self, maturity: float | date) -> float:
        ...

    def zero_rate(self, maturity: float | date) -> float:
        ...


@dataclass(frozen=True)
class FlatYieldCurve:
    """Flat continuously compounded yield curve."""

    rate: float
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_finite(self.rate, "rate")
        validate_date_configuration(self.reference_date, self.day_count)

    def discount(self, maturity: float | date) -> float:
        time = time_from_maturity(maturity, self.reference_date, self.day_count)
        return exp(-self.rate * time)

    def zero_rate(self, maturity: float | date) -> float:
        time_from_maturity(maturity, self.reference_date, self.day_count)
        return self.rate


@dataclass(frozen=True)
class ZeroCurve:
    """Interpolated continuously compounded zero-rate curve."""

    times: Sequence[float]
    zero_rates: Sequence[float]
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_curve_inputs(self.times, self.zero_rates, "zero_rates")
        validate_date_configuration(self.reference_date, self.day_count)

    def discount(self, maturity: float | date) -> float:
        time = time_from_maturity(maturity, self.reference_date, self.day_count)
        rate = self.zero_rate(time)
        return exp(-rate * time)

    def zero_rate(self, maturity: float | date) -> float:
        time = time_from_maturity(maturity, self.reference_date, self.day_count)
        return linear_interpolate(time, self.times, self.zero_rates)


@dataclass(frozen=True)
class DiscountCurve:
    """Interpolated discount curve using log-discount interpolation."""

    times: Sequence[float]
    discount_factors: Sequence[float]
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_curve_inputs(self.times, self.discount_factors, "discount_factors")
        if any(discount <= 0.0 for discount in self.discount_factors):
            raise ValueError("discount_factors must be positive")
        validate_date_configuration(self.reference_date, self.day_count)

    def discount(self, maturity: float | date) -> float:
        time = time_from_maturity(maturity, self.reference_date, self.day_count)
        log_discounts = [log(discount) for discount in self.discount_factors]
        return exp(linear_interpolate(time, self.times, log_discounts))

    def zero_rate(self, maturity: float | date) -> float:
        time = time_from_maturity(maturity, self.reference_date, self.day_count)
        if time == 0.0:
            raise ValueError("zero rate is undefined at time zero")
        return -log(self.discount(time)) / time


def _validate_curve_inputs(xs: Sequence[float], ys: Sequence[float], value_name: str) -> None:
    if len(xs) != len(ys):
        raise ValueError(f"times and {value_name} must have the same length")
    if len(xs) < 2:
        raise ValueError("at least two curve points are required")
    if any(not isfinite(time) for time in xs):
        raise ValueError("times must be finite")
    if any(time <= 0.0 for time in xs):
        raise ValueError("times must be positive")
    if any(xs[index] <= xs[index - 1] for index in range(1, len(xs))):
        raise ValueError("times must be strictly increasing")
    if any(not isfinite(value) for value in ys):
        raise ValueError(f"{value_name} must be finite")


def _validate_finite(value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
