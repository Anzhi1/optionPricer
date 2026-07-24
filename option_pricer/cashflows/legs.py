from option_pricer.cashflows.cashflow import Cashflow
from option_pricer.cashflows.fixed_rate import FixedRateCoupon
from option_pricer.cashflows.floating_rate import FloatingRateCoupon
from option_pricer.indexes.ibor import IborIndex
from option_pricer.schedules.schedule import Schedule
from option_pricer.time.daycounters import DayCounter


def fixed_rate_leg(
    *,
    schedule: Schedule,
    notional: float,
    fixed_rate: float,
    day_count: DayCounter,
) -> tuple[Cashflow, ...]:
    """Build fixed-rate coupons from adjacent schedule dates."""

    return tuple(
        FixedRateCoupon(
            accrual_start=schedule.dates[period_index - 1],
            accrual_end=schedule.dates[period_index],
            payment_date=schedule.dates[period_index],
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
) -> tuple[Cashflow, ...]:
    """Build floating-rate coupons from adjacent schedule dates."""

    return tuple(
        FloatingRateCoupon(
            accrual_start=schedule.dates[period_index - 1],
            accrual_end=schedule.dates[period_index],
            payment_date=schedule.dates[period_index],
            notional=notional,
            spread=spread,
            day_count=index.day_count,
            index=index,
        )
        for period_index in range(1, len(schedule.dates))
    )
