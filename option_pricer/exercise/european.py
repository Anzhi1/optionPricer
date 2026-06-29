from dataclasses import dataclass


@dataclass(frozen=True)
class EuropeanExercise:
    """European exercise at a positive year-fraction maturity."""

    maturity: float

    def __post_init__(self) -> None:
        if self.maturity <= 0:
            raise ValueError("maturity must be positive")
