from typing import Protocol


class Payoff(Protocol):
    """Maps an underlying value to a payoff amount."""

    def __call__(self, underlying: float) -> float:
        ...
