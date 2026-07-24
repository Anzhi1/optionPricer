from dataclasses import dataclass
from math import isfinite

from option_pricer.cashflows.cashflow import Cashflow, FixedCashflow
from option_pricer.cashflows.legs import fixed_rate_leg, floating_rate_leg
from option_pricer.indexes.ibor import IborIndex
from option_pricer.schedules.schedule import Schedule
from option_pricer.time.daycounters import DayCounter


@dataclass(frozen=True)
class FixedRateBond:
    """Simple fixed-rate bond represented by coupon and principal cashflows."""

    notional: float
    fixed_rate: float
    schedule: Schedule
    day_count: DayCounter

    def __post_init__(self) -> None:
        if not isfinite(self.notional):
            raise ValueError("notional must be finite")
        if self.notional <= 0.0:
            raise ValueError("notional must be positive")
        if not isfinite(self.fixed_rate):
            raise ValueError("fixed_rate must be finite")
        if not isinstance(self.schedule, Schedule):
            raise TypeError("schedule must be a Schedule")

    def cashflows(self) -> tuple[Cashflow, ...]:
        coupons = fixed_rate_leg(
            schedule=self.schedule,
            notional=self.notional,
            fixed_rate=self.fixed_rate,
            day_count=self.day_count,
        )
        redemption = FixedCashflow(payment_date=self.schedule.dates[-1], value=self.notional)
        return coupons + (redemption,)


@dataclass(frozen=True)
class FloatingRateNote:
    """Simple floating-rate note represented by floating coupons and principal."""

    notional: float
    spread: float
    schedule: Schedule
    index: IborIndex

    def __post_init__(self) -> None:
        if not isfinite(self.notional):
            raise ValueError("notional must be finite")
        if self.notional <= 0.0:
            raise ValueError("notional must be positive")
        if not isfinite(self.spread):
            raise ValueError("spread must be finite")
        if not isinstance(self.schedule, Schedule):
            raise TypeError("schedule must be a Schedule")

    def cashflows(self) -> tuple[Cashflow, ...]:
        coupons = floating_rate_leg(
            schedule=self.schedule,
            notional=self.notional,
            spread=self.spread,
            index=self.index,
        )
        redemption = FixedCashflow(payment_date=self.schedule.dates[-1], value=self.notional)
        return coupons + (redemption,)
