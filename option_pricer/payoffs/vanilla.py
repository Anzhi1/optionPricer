from dataclasses import dataclass
from enum import Enum


class OptionType(Enum):
    CALL = "call"
    PUT = "put"


@dataclass(frozen=True)
class PlainVanillaPayoff:
    """Plain call or put payoff with a positive strike."""

    option_type: OptionType
    strike: float

    def __post_init__(self) -> None:
        if not isinstance(self.option_type, OptionType):
            raise TypeError("option_type must be an OptionType")
        if self.strike <= 0:
            raise ValueError("strike must be positive")

    def __call__(self, underlying: float) -> float:
        if self.option_type is OptionType.CALL:
            return max(float(underlying) - self.strike, 0.0)
        return max(self.strike - float(underlying), 0.0)
