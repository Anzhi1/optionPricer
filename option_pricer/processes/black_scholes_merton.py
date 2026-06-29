from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class BlackScholesMertonProcess:
    """Black-Scholes-Merton process with flat continuously compounded inputs."""

    spot: float
    risk_free_rate: float
    dividend_yield: float
    volatility: float

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("spot must be positive")
        if self.volatility <= 0:
            raise ValueError("volatility must be positive")

    def discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.risk_free_rate * maturity)

    def dividend_discount_factor(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return exp(-self.dividend_yield * maturity)

    def forward(self, maturity: float) -> float:
        if maturity < 0:
            raise ValueError("maturity must be non-negative")
        return self.spot * exp((self.risk_free_rate - self.dividend_yield) * maturity)
