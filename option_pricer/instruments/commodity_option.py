from dataclasses import dataclass
from math import isfinite

from option_pricer.exercise.base import Exercise
from option_pricer.market.assets import Commodity
from option_pricer.market.currencies import Currency
from option_pricer.payoffs.vanilla import PlainVanillaPayoff


@dataclass(frozen=True)
class CommodityVanillaOption:
    """Vanilla option on a commodity or precious-metal forward price.

    Engine values are quote currency units per one commodity unit. Use
    `notional_value` to scale by an explicit commodity quantity.
    """

    commodity: Commodity
    currency: Currency
    payoff: PlainVanillaPayoff
    exercise: Exercise
    quantity: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.commodity, Commodity):
            raise TypeError("commodity must be a Commodity")
        if not isinstance(self.currency, Currency):
            raise TypeError("currency must be a Currency")
        if not isinstance(self.payoff, PlainVanillaPayoff):
            raise TypeError("payoff must be a PlainVanillaPayoff")
        maturity = getattr(self.exercise, "maturity", None)
        if maturity is None:
            raise TypeError("exercise must expose maturity")
        if maturity <= 0:
            raise ValueError("exercise maturity must be positive")
        if not isfinite(self.quantity):
            raise ValueError("quantity must be finite")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    def notional_value(self, unit_value: float) -> float:
        """Scale a per-unit option value to quote currency amount."""

        if not isfinite(unit_value):
            raise ValueError("unit_value must be finite")
        return unit_value * self.quantity
