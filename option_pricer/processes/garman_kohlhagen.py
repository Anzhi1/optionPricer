from dataclasses import dataclass
from datetime import date
from math import exp

from option_pricer.market.currencies import CurrencyPair
from option_pricer.market.quotes import SimpleQuote
from option_pricer.termstructures.volatility import BlackVolTermStructure
from option_pricer.termstructures.yield_curve import YieldTermStructure


@dataclass(frozen=True)
class GarmanKohlhagenProcess:
    """Garman-Kohlhagen FX process with flat continuously compounded inputs."""

    spot: float
    domestic_rate: float
    foreign_rate: float
    volatility: float
    pair: CurrencyPair | None = None

    @classmethod
    def from_term_structures(
        cls,
        *,
        spot: float | SimpleQuote,
        maturity: float | date,
        domestic_curve: YieldTermStructure,
        foreign_curve: YieldTermStructure,
        volatility: BlackVolTermStructure,
        pair: CurrencyPair | None = None,
        strike: float | None = None,
    ) -> "GarmanKohlhagenProcess":
        """Create a flat FX process snapshot from quote, curves, and volatility."""

        spot_value = spot.value if isinstance(spot, SimpleQuote) else float(spot)
        return cls(
            spot=spot_value,
            domestic_rate=domestic_curve.zero_rate(maturity),
            foreign_rate=foreign_curve.zero_rate(maturity),
            volatility=volatility.black_vol(maturity, strike=strike),
            pair=pair,
        )

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("spot must be positive")
        if self.volatility <= 0:
            raise ValueError("volatility must be positive")
        if self.pair is not None and not isinstance(self.pair, CurrencyPair):
            raise TypeError("pair must be a CurrencyPair")

    @property
    def risk_free_rate(self) -> float:
        """Domestic continuously compounded rate, for Black-Scholes compatibility."""

        return self.domestic_rate

    @property
    def dividend_yield(self) -> float:
        """Foreign continuously compounded rate, for Black-Scholes compatibility."""

        return self.foreign_rate

    @property
    def discount_rate(self) -> float:
        """Domestic continuously compounded discount rate."""

        return self.domestic_rate

    @property
    def carry_rate(self) -> float:
        """Foreign continuously compounded carry rate."""

        return self.foreign_rate

    def discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.domestic_rate * maturity)

    def foreign_discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.foreign_rate * maturity)

    def dividend_discount_factor(self, maturity: float) -> float:
        return self.foreign_discount_factor(maturity)

    def underlying_discount_factor(self, maturity: float) -> float:
        return self.foreign_discount_factor(maturity)

    def forward(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return self.spot * exp((self.domestic_rate - self.foreign_rate) * maturity)
