from datetime import date, timedelta
from enum import Enum

from option_pricer.time.calendars import Calendar


class BusinessDayConvention(Enum):
    FOLLOWING = "following"
    MODIFIED_FOLLOWING = "modified_following"
    PRECEDING = "preceding"
    UNADJUSTED = "unadjusted"


def adjust(day: date, calendar: Calendar, convention: BusinessDayConvention) -> date:
    """Adjust a date according to a business-day convention."""

    if not isinstance(convention, BusinessDayConvention):
        raise TypeError("convention must be a BusinessDayConvention")

    if convention is BusinessDayConvention.UNADJUSTED:
        return day
    if convention is BusinessDayConvention.FOLLOWING:
        return _following(day, calendar)
    if convention is BusinessDayConvention.PRECEDING:
        return _preceding(day, calendar)
    if convention is BusinessDayConvention.MODIFIED_FOLLOWING:
        following = _following(day, calendar)
        if following.month == day.month:
            return following
        return _preceding(day, calendar)

    raise ValueError(f"unsupported business-day convention: {convention}")


def _following(day: date, calendar: Calendar) -> date:
    adjusted = day
    while not calendar.is_business_day(adjusted):
        adjusted += timedelta(days=1)
    return adjusted


def _preceding(day: date, calendar: Calendar) -> date:
    adjusted = day
    while not calendar.is_business_day(adjusted):
        adjusted -= timedelta(days=1)
    return adjusted
