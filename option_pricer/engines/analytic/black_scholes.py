from dataclasses import dataclass
from math import log, sqrt
from typing import Protocol

from option_pricer.exercise.european import EuropeanExercise
from option_pricer.instruments.vanilla_option import VanillaOption
from option_pricer.math.distributions import normal_cdf, normal_pdf
from option_pricer.payoffs.vanilla import OptionType, PlainVanillaPayoff
from option_pricer.results.greeks import Greeks
from option_pricer.results.pricing_result import PricingResult


class BlackStyleProcess(Protocol):
    """Process interface needed by the analytic Black-style vanilla engine."""

    spot: float
    risk_free_rate: float
    dividend_yield: float
    volatility: float

    def discount_factor(self, maturity: float) -> float:
        ...

    def dividend_discount_factor(self, maturity: float) -> float:
        ...


@dataclass(frozen=True)
class AnalyticBlackScholesEngine:
    """Analytic Black-Scholes-Merton engine for European vanilla options."""

    process: BlackStyleProcess

    def calculate(self, instrument: VanillaOption) -> PricingResult:
        if not isinstance(instrument, VanillaOption):
            raise TypeError("AnalyticBlackScholesEngine supports VanillaOption only")
        if not isinstance(instrument.payoff, PlainVanillaPayoff):
            raise TypeError("AnalyticBlackScholesEngine supports PlainVanillaPayoff only")
        if not isinstance(instrument.exercise, EuropeanExercise):
            raise TypeError("AnalyticBlackScholesEngine supports EuropeanExercise only")

        payoff = instrument.payoff
        maturity = instrument.exercise.maturity
        d1, d2 = self._d1_d2(payoff.strike, maturity)

        spot = self.process.spot
        strike = payoff.strike
        rate = self.process.risk_free_rate
        dividend = self.process.dividend_yield
        volatility = self.process.volatility
        risk_discount = self.process.discount_factor(maturity)
        dividend_discount = self.process.dividend_discount_factor(maturity)

        if payoff.option_type is OptionType.CALL:
            value = spot * dividend_discount * normal_cdf(d1) - strike * risk_discount * normal_cdf(d2)
            delta = dividend_discount * normal_cdf(d1)
            theta = (
                -spot * dividend_discount * normal_pdf(d1) * volatility / (2.0 * sqrt(maturity))
                - rate * strike * risk_discount * normal_cdf(d2)
                + dividend * spot * dividend_discount * normal_cdf(d1)
            )
            rho = strike * maturity * risk_discount * normal_cdf(d2)
        else:
            value = strike * risk_discount * normal_cdf(-d2) - spot * dividend_discount * normal_cdf(-d1)
            delta = dividend_discount * (normal_cdf(d1) - 1.0)
            theta = (
                -spot * dividend_discount * normal_pdf(d1) * volatility / (2.0 * sqrt(maturity))
                + rate * strike * risk_discount * normal_cdf(-d2)
                - dividend * spot * dividend_discount * normal_cdf(-d1)
            )
            rho = -strike * maturity * risk_discount * normal_cdf(-d2)

        gamma = dividend_discount * normal_pdf(d1) / (spot * volatility * sqrt(maturity))
        vega = spot * dividend_discount * normal_pdf(d1) * sqrt(maturity)

        return PricingResult(
            value=value,
            greeks=Greeks(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho),
        )

    def _d1_d2(self, strike: float, maturity: float) -> tuple[float, float]:
        spot = self.process.spot
        rate = self.process.risk_free_rate
        dividend = self.process.dividend_yield
        volatility = self.process.volatility
        variance_root = volatility * sqrt(maturity)
        d1 = (log(spot / strike) + (rate - dividend + 0.5 * volatility * volatility) * maturity) / variance_root
        return d1, d1 - variance_root
