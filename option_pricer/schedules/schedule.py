from dataclasses import dataclass
from datetime import date
from enum import Enum

from option_pricer.time.business_day import BusinessDayConvention, adjust
from option_pricer.time.calendars import Calendar


class Frequency(Enum):
    """Coupon or schedule frequency."""

    ANNUAL = 12
    SEMIANNUAL = 6
    QUARTERLY = 3
    MONTHLY = 1


class DateGenerationRule(Enum):
    """Direction used to generate schedule dates."""

    FORWARD = "forward"
    BACKWARD = "backward"


@dataclass(frozen=True)
class Schedule:
    """Ordered adjusted schedule dates."""

    dates: tuple[date, ...]

    def __post_init__(self) -> None:
        if len(self.dates) < 2:
            raise ValueError("schedule must contain at least two dates")
        if any(not isinstance(schedule_date, date) for schedule_date in self.dates):
            raise TypeError("schedule dates must be date objects")
        if any(self.dates[index] <= self.dates[index - 1] for index in range(1, len(self.dates))):
            raise ValueError("schedule dates must be strictly increasing")


def generate_schedule(
    *,
    start_date: date,
    end_date: date,
    frequency: Frequency,
    calendar: Calendar,
    business_day_convention: BusinessDayConvention,
    date_generation_rule: DateGenerationRule = DateGenerationRule.FORWARD,
) -> Schedule:
    """Generate a minimal adjusted schedule."""

    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise TypeError("start_date and end_date must be date objects")
    if end_date <= start_date:
        raise ValueError("end_date must be after start_date")
    if not isinstance(frequency, Frequency):
        raise TypeError("frequency must be a Frequency")
    if not isinstance(date_generation_rule, DateGenerationRule):
        raise TypeError("date_generation_rule must be a DateGenerationRule")

    if date_generation_rule is DateGenerationRule.FORWARD:
        unadjusted_dates = _generate_forward_dates(start_date, end_date, frequency.value)
    else:
        unadjusted_dates = _generate_backward_dates(start_date, end_date, frequency.value)

    adjusted_dates = tuple(adjust(day, calendar, business_day_convention) for day in unadjusted_dates)
    return Schedule(dates=adjusted_dates)


def _generate_forward_dates(start_date: date, end_date: date, months: int) -> tuple[date, ...]:
    dates = [start_date]
    next_date = _add_months(start_date, months)
    while next_date < end_date:
        dates.append(next_date)
        next_date = _add_months(next_date, months)
    dates.append(end_date)
    return tuple(dates)


def _generate_backward_dates(start_date: date, end_date: date, months: int) -> tuple[date, ...]:
    dates = [end_date]
    previous_date = _add_months(end_date, -months)
    while previous_date > start_date:
        dates.append(previous_date)
        previous_date = _add_months(previous_date, -months)
    dates.append(start_date)
    return tuple(reversed(dates))


def _add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(day.day, _days_in_month(year, month)))


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - date(year, month, 1)).days
