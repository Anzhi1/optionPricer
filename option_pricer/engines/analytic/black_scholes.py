from dataclasses import dataclass
from math import log, sqrt

from option_pricer.exercise.european import EuropeanExercise
from option_pricer.instruments.commodity_option import CommodityVanillaOption
from option_pricer.instruments.fx_option import FxVanillaOption
from option_pricer.instruments.vanilla_option import VanillaOption
from option_pricer.math.distributions import normal_cdf, normal_pdf
from option_pricer.payoffs.vanilla import OptionType, PlainVanillaPayoff
from option_pricer.processes.black_style import BlackStyleProcess
from option_pricer.results.greeks import Greeks
from option_pricer.results.pricing_result import PricingResult


@dataclass(frozen=True)
class AnalyticBlackScholesEngine:
    """Analytic Black-Scholes-Merton engine for European vanilla options."""

    process: BlackStyleProcess

    def calculate(self, instrument: VanillaOption | FxVanillaOption | CommodityVanillaOption) -> PricingResult:
        payoff, maturity = self._vanilla_payoff_and_maturity(instrument)
        d1, d2 = self._d1_d2(payoff.strike, maturity)

        spot = self.process.spot
        strike = payoff.strike
        discount_rate = self.process.discount_rate
        carry_yield = discount_rate - self.process.underlying_growth_rate
        volatility = self.process.volatility
        discount_factor = self.process.discount_factor(maturity)
        underlying_discount = self.process.underlying_discount_factor(maturity)

        if payoff.option_type is OptionType.CALL:
            value = spot * underlying_discount * normal_cdf(d1) - strike * discount_factor * normal_cdf(d2)
            delta = underlying_discount * normal_cdf(d1)
            theta = (
                -spot * underlying_discount * normal_pdf(d1) * volatility / (2.0 * sqrt(maturity))
                - discount_rate * strike * discount_factor * normal_cdf(d2)
                + carry_yield * spot * underlying_discount * normal_cdf(d1)
            )
            rho = strike * maturity * discount_factor * normal_cdf(d2)
        else:
            value = strike * discount_factor * normal_cdf(-d2) - spot * underlying_discount * normal_cdf(-d1)
            delta = underlying_discount * (normal_cdf(d1) - 1.0)
            theta = (
                -spot * underlying_discount * normal_pdf(d1) * volatility / (2.0 * sqrt(maturity))
                + discount_rate * strike * discount_factor * normal_cdf(-d2)
                - carry_yield * spot * underlying_discount * normal_cdf(-d1)
            )
            rho = -strike * maturity * discount_factor * normal_cdf(-d2)

        gamma = underlying_discount * normal_pdf(d1) / (spot * volatility * sqrt(maturity))
        vega = spot * underlying_discount * normal_pdf(d1) * sqrt(maturity)

        return PricingResult(
            value=value,
            greeks=Greeks(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho),
        )

    def _d1_d2(self, strike: float, maturity: float) -> tuple[float, float]:
        spot = self.process.spot
        growth_rate = self.process.underlying_growth_rate
        volatility = self.process.volatility
        variance_root = volatility * sqrt(maturity)
        d1 = (
            log(spot / strike) + (growth_rate + 0.5 * volatility * volatility) * maturity
        ) / variance_root
        return d1, d1 - variance_root

    def _vanilla_payoff_and_maturity(
        self,
        instrument: VanillaOption | FxVanillaOption | CommodityVanillaOption,
    ) -> tuple[PlainVanillaPayoff, float]:
        if not isinstance(instrument, (VanillaOption, FxVanillaOption, CommodityVanillaOption)):
            raise TypeError(
                "AnalyticBlackScholesEngine supports VanillaOption, FxVanillaOption, "
                "and CommodityVanillaOption only"
            )
        if not isinstance(instrument.payoff, PlainVanillaPayoff):
            raise TypeError("AnalyticBlackScholesEngine supports PlainVanillaPayoff only")
        if not isinstance(instrument.exercise, EuropeanExercise):
            raise TypeError("AnalyticBlackScholesEngine supports EuropeanExercise only")
        return instrument.payoff, instrument.exercise.maturity
