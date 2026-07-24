from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Protocol

from option_pricer.math.interpolation import linear_interpolate
from option_pricer.termstructures.base import time_from_maturity, validate_date_configuration
from option_pricer.time.daycounters import DayCounter


class ForwardRateTermStructure(Protocol):
    """Simple forward-rate term structure."""

    def forward_rate(self, start: float | date, end: float | date) -> float:
        ...


@dataclass(frozen=True)
class FlatForwardRateCurve:
    """Flat simple annualized forward-rate curve."""

    rate: float
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_rate(self.rate)
        validate_date_configuration(self.reference_date, self.day_count)

    def forward_rate(self, start: float | date, end: float | date) -> float:
        _validate_forward_period(start, end, self.reference_date, self.day_count)
        return self.rate


@dataclass(frozen=True)
class ForwardRateCurve:
    """Interpolated simple annualized forward-rate curve by period end time."""

    times: Sequence[float]
    forward_rates: Sequence[float]
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_curve_inputs(self.times, self.forward_rates)
        validate_date_configuration(self.reference_date, self.day_count)

    def forward_rate(self, start: float | date, end: float | date) -> float:
        _, end_time = _validate_forward_period(start, end, self.reference_date, self.day_count)
        return linear_interpolate(end_time, self.times, self.forward_rates)


def _validate_forward_period(
    start: float | date,
    end: float | date,
    reference_date: date | None,
    day_count: DayCounter | None,
) -> tuple[float, float]:
    if isinstance(start, date) != isinstance(end, date):
        raise TypeError("start and end must both be dates or both be year fractions")

    start_time = time_from_maturity(start, reference_date, day_count)
    end_time = time_from_maturity(end, reference_date, day_count)
    if end_time <= start_time:
        raise ValueError("end must be after start")
    return start_time, end_time


def _validate_curve_inputs(times: Sequence[float], forward_rates: Sequence[float]) -> None:
    if len(times) != len(forward_rates):
        raise ValueError("times and forward_rates must have the same length")
    if len(times) < 2:
        raise ValueError("at least two forward-rate curve points are required")
    if any(not isfinite(time) for time in times):
        raise ValueError("times must be finite")
    if any(time <= 0.0 for time in times):
        raise ValueError("times must be positive")
    if any(times[index] <= times[index - 1] for index in range(1, len(times))):
        raise ValueError("times must be strictly increasing")
    for rate in forward_rates:
        _validate_rate(rate)


def _validate_rate(rate: float) -> None:
    if not isfinite(rate):
        raise ValueError("forward rate must be finite")
