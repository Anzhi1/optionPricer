from dataclasses import dataclass
from datetime import date
from math import exp

from option_pricer.market.quotes import SimpleQuote
from option_pricer.termstructures.volatility import BlackVolTermStructure
from option_pricer.termstructures.yield_curve import YieldTermStructure


@dataclass(frozen=True)
class BlackScholesMertonProcess:
    """Black-Scholes-Merton process with flat continuously compounded inputs."""

    spot: float
    risk_free_rate: float
    dividend_yield: float
    volatility: float

    @classmethod
    def from_term_structures(
        cls,
        *,
        spot: float | SimpleQuote,
        maturity: float | date,
        risk_free_curve: YieldTermStructure,
        dividend_curve: YieldTermStructure,
        volatility: BlackVolTermStructure,
        strike: float | None = None,
    ) -> "BlackScholesMertonProcess":
        """Create a flat process snapshot from quote, curve, and volatility inputs."""

        spot_value = spot.value if isinstance(spot, SimpleQuote) else float(spot)
        return cls(
            spot=spot_value,
            risk_free_rate=risk_free_curve.zero_rate(maturity),
            dividend_yield=dividend_curve.zero_rate(maturity),
            volatility=volatility.black_vol(maturity, strike=strike),
        )

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("spot must be positive")
        if self.volatility <= 0:
            raise ValueError("volatility must be positive")

    @property
    def discount_rate(self) -> float:
        """Continuously compounded discount rate for Black-style pricing."""

        return self.risk_free_rate

    @property
    def underlying_growth_rate(self) -> float:
        """Continuously compounded expected growth rate of the underlying."""

        return self.risk_free_rate - self.dividend_yield

    def discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.risk_free_rate * maturity)

    def underlying_discount_factor(self, maturity: float) -> float:
        return self.dividend_discount_factor(maturity)

    def dividend_discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.dividend_yield * maturity)

    def forward(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return self.spot * exp((self.risk_free_rate - self.dividend_yield) * maturity)
