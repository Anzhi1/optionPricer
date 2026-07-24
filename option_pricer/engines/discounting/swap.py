from dataclasses import dataclass

from option_pricer.engines.discounting.cashflows import DiscountingCashflowEngine
from option_pricer.instruments.rates.swaps import SwapType, VanillaInterestRateSwap
from option_pricer.results.pricing_result import PricingResult
from option_pricer.termstructures.yield_curve import YieldTermStructure


@dataclass(frozen=True)
class DiscountingSwapEngine:
    """Discounting engine for vanilla fixed-vs-floating interest-rate swaps."""

    discount_curve: YieldTermStructure

    def calculate(self, instrument: VanillaInterestRateSwap) -> PricingResult:
        if not isinstance(instrument, VanillaInterestRateSwap):
            raise TypeError("DiscountingSwapEngine supports VanillaInterestRateSwap only")

        cashflow_engine = DiscountingCashflowEngine(self.discount_curve)
        fixed_leg_pv = cashflow_engine.present_value(instrument.fixed_leg())
        floating_leg_pv = cashflow_engine.present_value(instrument.floating_leg())

        if instrument.swap_type is SwapType.PAYER:
            value = floating_leg_pv - fixed_leg_pv
        else:
            value = fixed_leg_pv - floating_leg_pv

        return PricingResult(
            value=value,
            diagnostics={
                "fixed_leg_pv": fixed_leg_pv,
                "floating_leg_pv": floating_leg_pv,
            },
        )
