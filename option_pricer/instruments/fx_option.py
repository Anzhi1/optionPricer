from dataclasses import dataclass

from option_pricer.exercise.base import Exercise
from option_pricer.market.currencies import CurrencyPair
from option_pricer.payoffs.vanilla import PlainVanillaPayoff


@dataclass(frozen=True)
class FxVanillaOption:
    """Vanilla FX option on a currency pair.

    Spot and strike are quoted as quote currency units per one base currency
    unit. The option value is in quote currency units per one base notional.
    """

    pair: CurrencyPair
    payoff: PlainVanillaPayoff
    exercise: Exercise

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
