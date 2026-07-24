from datetime import date

from option_pricer.cashflows.cashflow import Cashflow
from option_pricer.cashflows.fixed_rate import FixedRateCoupon
from option_pricer.cashflows.floating_rate import FloatingRateCoupon
from option_pricer.indexes.ibor import IborIndex
from option_pricer.schedules.schedule import Schedule
from option_pricer.time.business_day import BusinessDayConvention, adjust
from option_pricer.time.calendars import Calendar
from option_pricer.time.daycounters import DayCounter


def fixed_rate_leg(
    *,
    schedule: Schedule,
    notional: float,
    fixed_rate: float,
    day_count: DayCounter,
    payment_calendar: Calendar | None = None,
    payment_day_convention: BusinessDayConvention | None = None,
) -> tuple[Cashflow, ...]:
    """Build fixed-rate coupons from adjacent schedule dates."""

    _validate_payment_adjustment(payment_calendar, payment_day_convention)
    return tuple(
        FixedRateCoupon(
            accrual_start=schedule.dates[period_index - 1],
            accrual_end=schedule.dates[period_index],
            payment_date=_payment_date(
                schedule.dates[period_index],
                payment_calendar,
                payment_day_convention,
            ),
            notional=notional,
            fixed_rate=fixed_rate,
            day_count=day_count,
        )
        for period_index in range(1, len(schedule.dates))
    )


def floating_rate_leg(
    *,
    schedule: Schedule,
    notional: float,
    spread: float,
    index: IborIndex,
    payment_calendar: Calendar | None = None,
    payment_day_convention: BusinessDayConvention | None = None,
) -> tuple[Cashflow, ...]:
    """Build floating-rate coupons from adjacent schedule dates."""

    _validate_payment_adjustment(payment_calendar, payment_day_convention)
    return tuple(
        FloatingRateCoupon(
            accrual_start=schedule.dates[period_index - 1],
            accrual_end=schedule.dates[period_index],
            payment_date=_payment_date(
                schedule.dates[period_index],
                payment_calendar,
                payment_day_convention,
            ),
            notional=notional,
            spread=spread,
            day_count=index.day_count,
            index=index,
        )
        for period_index in range(1, len(schedule.dates))
    )


def _payment_date(
    accrual_end: date,
    payment_calendar: Calendar | None,
    payment_day_convention: BusinessDayConvention | None,
) -> date:
    if payment_calendar is None or payment_day_convention is None:
        return accrual_end
    return adjust(accrual_end, payment_calendar, payment_day_convention)


def _validate_payment_adjustment(
    payment_calendar: Calendar | None,
    payment_day_convention: BusinessDayConvention | None,
) -> None:
    if (payment_calendar is None) != (payment_day_convention is None):
        raise ValueError("payment_calendar and payment_day_convention must be provided together")
