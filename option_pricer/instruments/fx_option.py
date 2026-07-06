from dataclasses import dataclass
from math import isfinite

from option_pricer.exercise.base import Exercise
from option_pricer.market.currencies import CurrencyPair
from option_pricer.payoffs.vanilla import PlainVanillaPayoff


@dataclass(frozen=True)
class FxVanillaOption:
    """Vanilla FX option on a currency pair.

    Spot and strike are quoted as quote currency units per one base currency
    unit. Engine values are quote currency units per one base notional.
    """

    pair: CurrencyPair
    payoff: PlainVanillaPayoff
    exercise: Exercise
    notional: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.pair, CurrencyPair):
            raise TypeError("pair must be a CurrencyPair")
        if not isinstance(self.payoff, PlainVanillaPayoff):
            raise TypeError("payoff must be a PlainVanillaPayoff")
        maturity = getattr(self.exercise, "maturity", None)
        if maturity is None:
            raise TypeError("exercise must expose maturity")
        if maturity <= 0:
            raise ValueError("exercise maturity must be positive")
        if not isfinite(self.notional):
            raise ValueError("notional must be finite")
        if self.notional <= 0:
            raise ValueError("notional must be positive")

    def notional_value(self, unit_value: float) -> float:
        """Scale a per-base-notional unit value to quote currency amount."""

        if not isfinite(unit_value):
            raise ValueError("unit_value must be finite")
        return unit_value * self.notional
