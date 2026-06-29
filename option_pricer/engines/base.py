from typing import Protocol

from option_pricer.instruments.base import Instrument
from option_pricer.results.pricing_result import PricingResult


class PricingEngine(Protocol):
    """Calculates a pricing result for a supported instrument."""

    def calculate(self, instrument: Instrument) -> PricingResult:
        ...
