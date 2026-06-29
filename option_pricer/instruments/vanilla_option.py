from dataclasses import dataclass

from option_pricer.exercise.base import Exercise
from option_pricer.payoffs.base import Payoff


@dataclass(frozen=True)
class VanillaOption:
    """Vanilla option composed from a payoff and an exercise rule."""

    payoff: Payoff
    exercise: Exercise

    def __post_init__(self) -> None:
        if not callable(self.payoff):
            raise TypeError("payoff must be callable")
        maturity = getattr(self.exercise, "maturity", None)
        if maturity is None:
            raise TypeError("exercise must expose maturity")
        if maturity <= 0:
            raise ValueError("exercise maturity must be positive")
