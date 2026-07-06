from datetime import date
from math import isfinite

from option_pricer.time.daycounters import DayCounter


def time_from_maturity(
    maturity: float | date,
    reference_date: date | None,
    day_count: DayCounter | None,
) -> float:
    """Convert a year-fraction or date maturity to a non-negative time."""

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


def validate_date_configuration(reference_date: date | None, day_count: DayCounter | None) -> None:
    """Validate that date-based term structures have complete date configuration."""

    if (reference_date is None) != (day_count is None):
        raise ValueError("reference_date and day_count must be provided together")
