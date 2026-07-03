from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Protocol

from option_pricer.math.interpolation import linear_interpolate
from option_pricer.time.daycounters import DayCounter


class BlackVolTermStructure(Protocol):
    """Black volatility term structure."""

    def black_vol(self, maturity: float | date, strike: float | None = None) -> float:
        ...


@dataclass(frozen=True)
class FlatBlackVolatility:
    """Flat Black volatility term structure."""

    volatility: float
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_volatility(self.volatility)
        _validate_date_configuration(self.reference_date, self.day_count)

    def black_vol(self, maturity: float | date, strike: float | None = None) -> float:
        _time_from_maturity(maturity, self.reference_date, self.day_count)
        return self.volatility


FlatVolatility = FlatBlackVolatility


@dataclass(frozen=True)
class BlackVolCurve:
    """Interpolated Black volatility curve with no strike dependence."""

    times: Sequence[float]
    volatilities: Sequence[float]
    reference_date: date | None = None
    day_count: DayCounter | None = None

    def __post_init__(self) -> None:
        _validate_curve_inputs(self.times, self.volatilities)
        _validate_date_configuration(self.reference_date, self.day_count)

    def black_vol(self, maturity: float | date, strike: float | None = None) -> float:
        time = _time_from_maturity(maturity, self.reference_date, self.day_count)
        return linear_interpolate(time, self.times, self.volatilities)


def _time_from_maturity(
    maturity: float | date,
    reference_date: date | None,
    day_count: DayCounter | None,
) -> float:
    if isinstance(maturity, date):
        if reference_date is None or day_count is None:
            raise ValueError("date maturity requires reference_date and day_count")
        time = day_count.year_fraction(reference_date, maturity)
    else:
        time = float(maturity)

    if not isfinite(time):
        raise ValueError("maturity must be finite")
    if time < 0.0:
        raise ValueError("maturity must be non-negative")
    return time


def _validate_date_configuration(reference_date: date | None, day_count: DayCounter | None) -> None:
    if (reference_date is None) != (day_count is None):
        raise ValueError("reference_date and day_count must be provided together")


def _validate_curve_inputs(times: Sequence[float], volatilities: Sequence[float]) -> None:
    if len(times) != len(volatilities):
        raise ValueError("times and volatilities must have the same length")
    if len(times) < 2:
        raise ValueError("at least two volatility points are required")
    if any(not isfinite(time) for time in times):
        raise ValueError("times must be finite")
    if any(time <= 0.0 for time in times):
        raise ValueError("times must be positive")
    if any(times[index] <= times[index - 1] for index in range(1, len(times))):
        raise ValueError("times must be strictly increasing")
    for volatility in volatilities:
        _validate_volatility(volatility)


def _validate_volatility(volatility: float) -> None:
    if not isfinite(volatility):
        raise ValueError("volatility must be finite")
    if volatility <= 0.0:
        raise ValueError("volatility must be positive")
