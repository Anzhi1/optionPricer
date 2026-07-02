from dataclasses import dataclass
from datetime import date
from typing import Protocol


class DayCounter(Protocol):
    """Calculates year fractions between two dates."""

    @property
    def name(self) -> str:
        ...

    def year_fraction(self, start: date, end: date) -> float:
        ...


def _validate_date_order(start: date, end: date) -> None:
    if end < start:
        raise ValueError("end date must be greater than or equal to start date")


@dataclass(frozen=True)
class Actual365Fixed:
    """Actual/365 Fixed day-count convention."""

    name: str = "Actual/365 Fixed"

    def year_fraction(self, start: date, end: date) -> float:
        _validate_date_order(start, end)
        return (end - start).days / 365.0


@dataclass(frozen=True)
class Actual360:
    """Actual/360 day-count convention."""

    name: str = "Actual/360"

    def year_fraction(self, start: date, end: date) -> float:
        _validate_date_order(start, end)
        return (end - start).days / 360.0
