from dataclasses import dataclass
from math import sqrt

from option_pricer.exercise.european import EuropeanExercise
from option_pricer.instruments.vanilla_option import VanillaOption
from option_pricer.payoffs.vanilla import PlainVanillaPayoff
from option_pricer.processes.black_style import BlackStyleProcess
from option_pricer.results.pricing_result import PricingResult


@dataclass(frozen=True)
class EuropeanMonteCarloEngine:
    """Terminal lognormal Monte Carlo engine for European Black-style vanilla options."""

    process: BlackStyleProcess
    paths: int = 100_000
    seed: int | None = None
    antithetic: bool = False

    def __post_init__(self) -> None:
        if self.paths <= 0:
            raise ValueError("paths must be positive")
        if self.antithetic and self.paths % 2 != 0:
            raise ValueError("paths must be even when antithetic is enabled")

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
            half_paths = self.paths // 2
            normals = rng.standard_normal(half_paths)
            normals = np.concatenate([normals, -normals])
        else:
            normals = rng.standard_normal(self.paths)

        drift = (
            self.process.discount_rate
            - self.process.carry_rate
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
        if self.antithetic:
            pair_averages = 0.5 * (discounted[:half_paths] + discounted[half_paths:])
            standard_error = (
                float(np.std(pair_averages, ddof=1) / sqrt(half_paths))
                if half_paths > 1
                else 0.0
            )
        else:
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
