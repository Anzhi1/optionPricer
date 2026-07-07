from dataclasses import dataclass
from datetime import date
from math import exp

from option_pricer.market.quotes import SimpleQuote
from option_pricer.termstructures.forward_curve import ForwardTermStructure
from option_pricer.termstructures.volatility import BlackVolTermStructure
from option_pricer.termstructures.yield_curve import YieldTermStructure


@dataclass(frozen=True)
class Black76Process:
    """Black-76 process for options on forwards or futures."""

    forward: float
    discount_rate_value: float
    volatility: float

    @classmethod
    def from_term_structures(
        cls,
        *,
        forward: float | SimpleQuote,
        maturity: float | date,
        discount_curve: YieldTermStructure,
        volatility: BlackVolTermStructure,
        strike: float | None = None,
    ) -> "Black76Process":
        """Create a flat Black-76 process snapshot from forward, curve, and volatility."""

        forward_value = forward.value if isinstance(forward, SimpleQuote) else float(forward)
        return cls(
            forward=forward_value,
            discount_rate_value=discount_curve.zero_rate(maturity),
            volatility=volatility.black_vol(maturity, strike=strike),
        )

    @classmethod
    def from_forward_curve(
        cls,
        *,
        forward_curve: ForwardTermStructure,
        maturity: float | date,
        discount_curve: YieldTermStructure,
        volatility: BlackVolTermStructure,
        strike: float | None = None,
    ) -> "Black76Process":
        """Create a flat Black-76 snapshot from forward, discount, and volatility curves."""

        return cls(
            forward=forward_curve.forward(maturity),
            discount_rate_value=discount_curve.zero_rate(maturity),
            volatility=volatility.black_vol(maturity, strike=strike),
        )

    def __post_init__(self) -> None:
        if self.forward <= 0:
            raise ValueError("forward must be positive")
        if self.volatility <= 0:
            raise ValueError("volatility must be positive")

    @property
    def spot(self) -> float:
        """Forward value exposed as the Black-style underlying input."""

        return self.forward

    @property
    def discount_rate(self) -> float:
        return self.discount_rate_value

    @property
    def underlying_growth_rate(self) -> float:
        return 0.0

    def discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.discount_rate_value * maturity)

    def underlying_discount_factor(self, maturity: float) -> float:
        return self.discount_factor(maturity)
