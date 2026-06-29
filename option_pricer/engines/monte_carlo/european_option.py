from dataclasses import dataclass
from math import exp, sqrt

from option_pricer.exercise.european import EuropeanExercise
from option_pricer.instruments.vanilla_option import VanillaOption
from option_pricer.payoffs.vanilla import PlainVanillaPayoff
from option_pricer.processes.black_scholes_merton import BlackScholesMertonProcess
from option_pricer.results.pricing_result import PricingResult


@dataclass(frozen=True)
class EuropeanMonteCarloEngine:
    """Terminal-spot Monte Carlo engine for European vanilla options."""

    process: BlackScholesMertonProcess
    paths: int = 100_000
    seed: int | None = None
    antithetic: bool = False

    def __post_init__(self) -> None:
        if self.paths <= 0:
            raise ValueError("paths must be positive")

    def calculate(self, instrument: VanillaOption) -> PricingResult:
        if not isinstance(instrument, VanillaOption):
            raise TypeError("EuropeanMonteCarloEngine supports VanillaOption only")
        if not isinstance(instrument.payoff, PlainVanillaPayoff):
            raise TypeError("EuropeanMonteCarloEngine supports PlainVanillaPayoff only")
        if not isinstance(instrument.exercise, EuropeanExercise):
            raise TypeError("EuropeanMonteCarloEngine supports EuropeanExercise only")

        try:
            import numpy as np
        except ImportError as exc:
            raise ImportError("EuropeanMonteCarloEngine requires numpy") from exc

        maturity = instrument.exercise.maturity
        rng = np.random.default_rng(self.seed)
        if self.antithetic:
            half_paths = (self.paths + 1) // 2
            normals = rng.standard_normal(half_paths)
            normals = np.concatenate([normals, -normals])[: self.paths]
        else:
            normals = rng.standard_normal(self.paths)

        drift = (
            self.process.risk_free_rate
            - self.process.dividend_yield
            - 0.5 * self.process.volatility * self.process.volatility
        ) * maturity
        diffusion = self.process.volatility * sqrt(maturity) * normals
        terminal_spots = self.process.spot * np.exp(drift + diffusion)
        payoffs = np.maximum(
            np.fromiter((instrument.payoff(float(spot)) for spot in terminal_spots), dtype=float),
            0.0,
        )
        discounted = self.process.discount_factor(maturity) * payoffs
        value = float(np.mean(discounted))
        standard_error = float(np.std(discounted, ddof=1) / sqrt(self.paths)) if self.paths > 1 else 0.0

        return PricingResult(
            value=value,
            diagnostics={
                "paths": self.paths,
                "seed": self.seed,
                "antithetic": self.antithetic,
                "standard_error": standard_error,
            },
        )
