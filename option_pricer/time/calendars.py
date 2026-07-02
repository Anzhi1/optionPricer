from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


class Calendar(Protocol):
    """Determines whether dates are business days."""

    @property
    def name(self) -> str:
        ...

    def is_business_day(self, day: date) -> bool:
        ...


@dataclass(frozen=True)
class NullCalendar:
    """Calendar where every date is a business day."""

    name: str = "Null"

    def is_business_day(self, day: date) -> bool:
        return True


@dataclass(frozen=True)
class WeekendCalendar:
    """Calendar where configured weekend weekdays are not business days."""

    name: str = "Weekend"
    weekend_days: frozenset[int] = field(default_factory=lambda: frozenset({5, 6}))

    def __post_init__(self) -> None:
        _validate_weekend_days(self.weekend_days)

    def is_business_day(self, day: date) -> bool:
        return day.weekday() not in self.weekend_days


@dataclass(frozen=True)
class HolidayCalendar:
    """Calendar with explicit holidays and configurable weekend weekdays."""

    name: str
    holidays: frozenset[date] = field(default_factory=frozenset)
    weekend_days: frozenset[int] = field(default_factory=lambda: frozenset({5, 6}))

    def __post_init__(self) -> None:
        _validate_weekend_days(self.weekend_days)
        if not all(isinstance(holiday, date) for holiday in self.holidays):
            raise TypeError("holidays must contain date objects")

    def is_business_day(self, day: date) -> bool:
        return day.weekday() not in self.weekend_days and day not in self.holidays


def _validate_weekend_days(weekend_days: frozenset[int]) -> None:
    if not all(isinstance(day, int) for day in weekend_days):
        raise TypeError("weekend days must be integers")
    if not all(0 <= day <= 6 for day in weekend_days):
        raise ValueError("weekend days must be between 0 and 6")
