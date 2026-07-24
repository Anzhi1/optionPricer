from dataclasses import dataclass

from option_pricer.engines.discounting.cashflows import DiscountingCashflowEngine
from option_pricer.instruments.rates.bonds import FixedRateBond
from option_pricer.results.pricing_result import PricingResult
from option_pricer.termstructures.yield_curve import YieldTermStructure


@dataclass(frozen=True)
class DiscountingBondEngine:
    """Discounting engine for fixed-rate bonds."""

    discount_curve: YieldTermStructure

    def calculate(self, instrument: FixedRateBond) -> PricingResult:
        if not isinstance(instrument, FixedRateBond):
            raise TypeError("DiscountingBondEngine supports FixedRateBond only")
        value = DiscountingCashflowEngine(self.discount_curve).present_value(instrument.cashflows())
        return PricingResult(value=value)
