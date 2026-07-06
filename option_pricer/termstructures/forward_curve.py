from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Protocol

from option_pricer.math.interpolation import linear_interpolate
from option_pricer.termstructures.base import time_from_maturity, validate_date_configuration
from option_pricer.time.daycounters import DayCounter


class ForwardTermStructure(Protocol):
    """Forward price term structure."""

    def forward(self, maturity: float | date) -> float:
        ...


@dataclass(frozen=True)
class FlatForwardCurve:
    """Flat forward price curve."""

    forward_value: float
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_forward(self.forward_value)
        validate_date_configuration(self.reference_date, self.day_count)

    def forward(self, maturity: float | date) -> float:
        time_from_maturity(maturity, self.reference_date, self.day_count)
        return self.forward_value


@dataclass(frozen=True)
class ForwardCurve:
    """Interpolated forward price curve."""

    times: Sequence[float]
    forwards: Sequence[float]
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_curve_inputs(self.times, self.forwards)
        validate_date_configuration(self.reference_date, self.day_count)

    def forward(self, maturity: float | date) -> float:
        time = time_from_maturity(maturity, self.reference_date, self.day_count)
        return linear_interpolate(time, self.times, self.forwards)


def _validate_curve_inputs(times: Sequence[float], forwards: Sequence[float]) -> None:
    if len(times) != len(forwards):
        raise ValueError("times and forwards must have the same length")
    if len(times) < 2:
        raise ValueError("at least two forward curve points are required")
    if any(not isfinite(time) for time in times):
        raise ValueError("times must be finite")
    if any(time <= 0.0 for time in times):
        raise ValueError("times must be positive")
    if any(times[index] <= times[index - 1] for index in range(1, len(times))):
        raise ValueError("times must be strictly increasing")
    for forward in forwards:
        _validate_forward(forward)


def _validate_forward(forward: float) -> None:
    if not isfinite(forward):
        raise ValueError("forward must be finite")
    if forward <= 0.0:
        raise ValueError("forward must be positive")
