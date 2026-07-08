from datetime import date

import pytest

from option_pricer import (
    BusinessDayConvention,
    DateGenerationRule,
    Frequency,
    NullCalendar,
    Schedule,
    WeekendCalendar,
    generate_schedule,
)


def test_generate_annual_forward_schedule() -> None:
    schedule = generate_schedule(
        start_date=date(2026, 1, 15),
        end_date=date(2029, 1, 15),
        frequency=Frequency.ANNUAL,
        calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
    )

    assert schedule.dates == (
        date(2026, 1, 15),
        date(2027, 1, 15),
        date(2028, 1, 15),
        date(2029, 1, 15),
    )


def test_generate_semiannual_backward_schedule() -> None:
    schedule = generate_schedule(
        start_date=date(2026, 1, 15),
        end_date=date(2027, 1, 15),
        frequency=Frequency.SEMIANNUAL,
        calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
        date_generation_rule=DateGenerationRule.BACKWARD,
    )

    assert schedule.dates == (
        date(2026, 1, 15),
        date(2026, 7, 15),
        date(2027, 1, 15),
    )


def test_generate_schedule_applies_business_day_adjustment() -> None:
    schedule = generate_schedule(
        start_date=date(2026, 7, 4),
        end_date=date(2027, 7, 4),
        frequency=Frequency.ANNUAL,
        calendar=WeekendCalendar(),
        business_day_convention=BusinessDayConvention.FOLLOWING,
    )

    assert schedule.dates == (date(2026, 7, 6), date(2027, 7, 5))


def test_generate_monthly_schedule_handles_short_month() -> None:
    schedule = generate_schedule(
        start_date=date(2026, 1, 31),
        end_date=date(2026, 4, 30),
        frequency=Frequency.MONTHLY,
        calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
    )

    assert schedule.dates == (
        date(2026, 1, 31),
        date(2026, 2, 28),
        date(2026, 3, 28),
        date(2026, 4, 28),
        date(2026, 4, 30),
    )


def test_generate_schedule_rejects_invalid_date_order() -> None:
    with pytest.raises(ValueError, match="end_date"):
        generate_schedule(
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 15),
            frequency=Frequency.ANNUAL,
            calendar=NullCalendar(),
            business_day_convention=BusinessDayConvention.UNADJUSTED,
        )


def test_generate_schedule_rejects_invalid_frequency() -> None:
    with pytest.raises(TypeError, match="Frequency"):
        generate_schedule(
            start_date=date(2026, 1, 15),
            end_date=date(2027, 1, 15),
            frequency="annual",  # type: ignore[arg-type]
            calendar=NullCalendar(),
            business_day_convention=BusinessDayConvention.UNADJUSTED,
        )


def test_schedule_rejects_non_increasing_dates() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        Schedule(dates=(date(2026, 1, 15), date(2026, 1, 15)))
