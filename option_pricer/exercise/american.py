from dataclasses import dataclass


@dataclass(frozen=True)
class AmericanExercise:
    """American exercise from valuation time to a positive year-fraction maturity."""

    maturity: float

    def __post_init__(self) -> None:
        if self.maturity <= 0:
            raise ValueError("maturity must be positive")
