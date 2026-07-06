from typing import Protocol


class BlackStyleProcess(Protocol):
    """Lognormal Black-style process interface used by vanilla Black engines."""

    spot: float
    volatility: float

    @property
    def discount_rate(self) -> float:
        ...

    @property
    def carry_rate(self) -> float:
        ...

    def discount_factor(self, maturity: float) -> float:
        ...

    def underlying_discount_factor(self, maturity: float) -> float:
        ...
