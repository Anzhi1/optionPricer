from dataclasses import dataclass
from enum import Enum
from math import isfinite

from option_pricer.cashflows.cashflow import Cashflow
from option_pricer.cashflows.fixed_rate import FixedRateCoupon
from option_pricer.cashflows.floating_rate import FloatingRateCoupon
from option_pricer.indexes.ibor import IborIndex
from option_pricer.schedules.schedule import Schedule
from option_pricer.time.daycounters import DayCounter


class SwapType(Enum):
    """Fixed-leg direction for a vanilla interest-rate swap."""

    PAYER = "payer"
    RECEIVER = "receiver"


@dataclass(frozen=True)
class VanillaInterestRateSwap:
    """Vanilla fixed-vs-floating interest-rate swap without notional exchange."""

    swap_type: SwapType
    notional: float
    fixed_rate: float
    fixed_schedule: Schedule
    fixed_day_count: DayCounter
    floating_schedule: Schedule
    index: IborIndex
    spread: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.swap_type, SwapType):
            raise TypeError("swap_type must be a SwapType")
        if not isfinite(self.notional):
            raise ValueError("notional must be finite")
        if self.notional <= 0.0:
            raise ValueError("notional must be positive")
        if not isfinite(self.fixed_rate):
            raise ValueError("fixed_rate must be finite")
        if not isfinite(self.spread):
            raise ValueError("spread must be finite")
        if not isinstance(self.fixed_schedule, Schedule):
            raise TypeError("fixed_schedule must be a Schedule")
        if not isinstance(self.floating_schedule, Schedule):
            raise TypeError("floating_schedule must be a Schedule")

    def fixed_leg(self) -> tuple[Cashflow, ...]:
        return tuple(
            FixedRateCoupon(
                accrual_start=self.fixed_schedule.dates[index - 1],
                accrual_end=self.fixed_schedule.dates[index],
                payment_date=self.fixed_schedule.dates[index],
                notional=self.notional,
                fixed_rate=self.fixed_rate,
                day_count=self.fixed_day_count,
            )
            for index in range(1, len(self.fixed_schedule.dates))
        )

    def floating_leg(self) -> tuple[Cashflow, ...]:
        return tuple(
            FloatingRateCoupon(
                accrual_start=self.floating_schedule.dates[index - 1],
                accrual_end=self.floating_schedule.dates[index],
                payment_date=self.floating_schedule.dates[index],
                notional=self.notional,
                spread=self.spread,
                day_count=self.index.day_count,
                index=self.index,
            )
            for index in range(1, len(self.floating_schedule.dates))
        )
