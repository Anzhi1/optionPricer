from datetime import date

import pytest

from option_pricer import (
    Actual360,
    Actual365Fixed,
    BusinessDayConvention,
    HolidayCalendar,
    NullCalendar,
    WeekendCalendar,
    adjust,
)


def test_actual_365_fixed_year_fraction() -> None:
    day_count = Actual365Fixed()

    assert day_count.name == "Actual/365 Fixed"
    assert day_count.year_fraction(date(2026, 1, 1), date(2027, 1, 1)) == pytest.approx(1.0)


def test_actual_360_year_fraction() -> None:
    day_count = Actual360()

    assert day_count.name == "Actual/360"
    assert day_count.year_fraction(date(2026, 1, 1), date(2026, 7, 1)) == pytest.approx(181 / 360)


def test_day_counter_rejects_reversed_dates() -> None:
    with pytest.raises(ValueError, match="end date"):
        Actual365Fixed().year_fraction(date(2027, 1, 1), date(2026, 1, 1))


def test_null_calendar_treats_every_day_as_business_day() -> None:
    calendar = NullCalendar()

    assert calendar.is_business_day(date(2026, 7, 4))
    assert calendar.is_business_day(date(2026, 7, 5))


def test_weekend_calendar_rejects_weekends() -> None:
    calendar = WeekendCalendar()

    assert calendar.is_business_day(date(2026, 7, 3))
    assert not calendar.is_business_day(date(2026, 7, 4))
    assert not calendar.is_business_day(date(2026, 7, 5))


def test_holiday_calendar_rejects_explicit_holidays() -> None:
    calendar = HolidayCalendar(
        name="Example",
        holidays=frozenset({date(2026, 10, 1)}),
    )

    assert calendar.is_business_day(date(2026, 9, 30))
    assert not calendar.is_business_day(date(2026, 10, 1))
    assert not calendar.is_business_day(date(2026, 10, 3))


def test_calendar_validates_weekend_days() -> None:
    with pytest.raises(ValueError, match="between 0 and 6"):
        WeekendCalendar(weekend_days=frozenset({7}))

    with pytest.raises(TypeError, match="integers"):
        WeekendCalendar(weekend_days=frozenset({"Saturday"}))  # type: ignore[arg-type]


def test_holiday_calendar_validates_holiday_types() -> None:
    with pytest.raises(TypeError, match="date objects"):
        HolidayCalendar(name="Bad", holidays=frozenset({"2026-01-01"}))  # type: ignore[arg-type]


def test_following_adjustment() -> None:
    calendar = WeekendCalendar()

    assert adjust(
        date(2026, 7, 4),
        calendar,
        BusinessDayConvention.FOLLOWING,
    ) == date(2026, 7, 6)


def test_preceding_adjustment() -> None:
    calendar = WeekendCalendar()

    assert adjust(
        date(2026, 7, 4),
        calendar,
        BusinessDayConvention.PRECEDING,
    ) == date(2026, 7, 3)


def test_modified_following_adjustment_keeps_same_month_when_possible() -> None:
    calendar = WeekendCalendar()

    assert adjust(
        date(2026, 7, 4),
        calendar,
        BusinessDayConvention.MODIFIED_FOLLOWING,
    ) == date(2026, 7, 6)


def test_modified_following_adjustment_falls_back_when_month_changes() -> None:
    calendar = WeekendCalendar()

    assert adjust(
        date(2026, 1, 31),
        calendar,
        BusinessDayConvention.MODIFIED_FOLLOWING,
    ) == date(2026, 1, 30)


def test_unadjusted_returns_original_date() -> None:
    calendar = WeekendCalendar()
    original = date(2026, 7, 4)

    assert adjust(original, calendar, BusinessDayConvention.UNADJUSTED) == original


def test_adjust_rejects_invalid_convention() -> None:
    with pytest.raises(TypeError, match="BusinessDayConvention"):
        adjust(date(2026, 7, 4), WeekendCalendar(), "following")  # type: ignore[arg-type]
