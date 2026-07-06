from dataclasses import dataclass
from datetime import date

from option_pricer.time.daycounters import DayCounter


@dataclass(frozen=True)
class AmericanExercise:
    """American exercise from valuation time to a positive year-fraction maturity."""

    maturity: float

    @classmethod
    def from_dates(
        cls,
        *,
        evaluation_date: date,
        expiry_date: date,
        day_count: DayCounter,
    ) -> "AmericanExercise":
        """Create American exercise by converting dates to a year fraction."""

        return cls(maturity=day_count.year_fraction(evaluation_date, expiry_date))

    def __post_init__(self) -> None:
        if self.maturity <= 0:
            raise ValueError("maturity must be positive")
