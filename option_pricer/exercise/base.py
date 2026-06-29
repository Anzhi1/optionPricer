from typing import Protocol


class Exercise(Protocol):
    """Exercise rule represented by year-fraction maturity in Phase 1."""

    @property
    def maturity(self) -> float:
        ...
