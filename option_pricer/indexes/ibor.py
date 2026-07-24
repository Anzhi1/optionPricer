from dataclasses import dataclass
from datetime import date

from option_pricer.termstructures.forward_rate_curve import ForwardRateTermStructure
from option_pricer.time.business_day import BusinessDayConvention, adjust
from option_pricer.time.calendars import Calendar
from option_pricer.time.daycounters import DayCounter


@dataclass(frozen=True)
class IborIndex:
    """Lightweight Ibor-style index for projected floating rates."""

    name: str
    tenor_months: int
    day_count: DayCounter
    fixing_calendar: Calendar
    business_day_convention: BusinessDayConvention
    projection_curve: ForwardRateTermStructure

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be non-empty")
        if not isinstance(self.tenor_months, int):
            raise TypeError("tenor_months must be an integer")
        if self.tenor_months <= 0:
            raise ValueError("tenor_months must be positive")
        if not isinstance(self.business_day_convention, BusinessDayConvention):
            raise TypeError("business_day_convention must be a BusinessDayConvention")

    def fixing_date(self, accrual_start: date) -> date:
        return adjust(accrual_start, self.fixing_calendar, self.business_day_convention)

    def rate(self, accrual_start: date, accrual_end: date) -> float:
        return self.projection_curve.forward_rate(accrual_start, accrual_end)
