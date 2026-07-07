from dataclasses import dataclass
from math import exp, sqrt

from option_pricer.exercise.american import AmericanExercise
from option_pricer.exercise.european import EuropeanExercise
from option_pricer.instruments.vanilla_option import VanillaOption
from option_pricer.payoffs.vanilla import PlainVanillaPayoff
from option_pricer.processes.black_style import BlackStyleProcess
from option_pricer.results.pricing_result import PricingResult


@dataclass(frozen=True)
class BinomialTreeEngine:
    """Cox-Ross-Rubinstein tree engine for Black-style vanilla options."""

    process: BlackStyleProcess
    steps: int = 200

    def __post_init__(self) -> None:
        if self.steps <= 0:
            raise ValueError("steps must be positive")

    def calculate(self, instrument: VanillaOption) -> PricingResult:
        if not isinstance(instrument, VanillaOption):
            raise TypeError("BinomialTreeEngine supports VanillaOption only")
        if not isinstance(instrument.payoff, PlainVanillaPayoff):
            raise TypeError("BinomialTreeEngine supports PlainVanillaPayoff only")
        if not isinstance(instrument.exercise, (EuropeanExercise, AmericanExercise)):
            raise TypeError("BinomialTreeEngine supports EuropeanExercise or AmericanExercise only")

        maturity = instrument.exercise.maturity
        dt = maturity / self.steps
        up = exp(self.process.volatility * sqrt(dt))
        down = 1.0 / up
        growth = exp(self.process.underlying_growth_rate * dt)
        probability = (growth - down) / (up - down)
        if not 0.0 <= probability <= 1.0:
            raise ValueError("tree risk-neutral probability is outside [0, 1]")

        step_discount = exp(-self.process.discount_rate * dt)
        values = [
            instrument.payoff(self.process.spot * (up ** j) * (down ** (self.steps - j)))
            for j in range(self.steps + 1)
        ]

        is_american = isinstance(instrument.exercise, AmericanExercise)
        for step in range(self.steps - 1, -1, -1):
            next_values = []
            for node in range(step + 1):
                continuation = step_discount * (
                    probability * values[node + 1] + (1.0 - probability) * values[node]
                )
                if is_american:
                    spot = self.process.spot * (up ** node) * (down ** (step - node))
                    continuation = max(continuation, instrument.payoff(spot))
                next_values.append(continuation)
            values = next_values

        return PricingResult(value=values[0], diagnostics={"steps": self.steps})
