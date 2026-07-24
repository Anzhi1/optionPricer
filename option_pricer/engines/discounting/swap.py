from dataclasses import dataclass
from math import isfinite

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
                "fair_rate": self.fair_rate(instrument),
            },
        )

    def fixed_leg_annuity(self, instrument: VanillaInterestRateSwap) -> float:
        """Return the PV of one unit of fixed rate on the swap fixed leg."""

        if not isinstance(instrument, VanillaInterestRateSwap):
            raise TypeError("DiscountingSwapEngine supports VanillaInterestRateSwap only")

        annuity = sum(
            instrument.notional
            * instrument.fixed_day_count.year_fraction(
                instrument.fixed_schedule.dates[index - 1],
                instrument.fixed_schedule.dates[index],
            )
            * self.discount_curve.discount(instrument.fixed_schedule.dates[index])
            for index in range(1, len(instrument.fixed_schedule.dates))
        )
        if not isfinite(annuity):
            raise ValueError("fixed leg annuity must be finite")
        if annuity <= 0.0:
            raise ValueError("fixed leg annuity must be positive")
        return annuity

    def fair_rate(self, instrument: VanillaInterestRateSwap) -> float:
        """Return the fixed rate that makes the swap value zero."""

        if not isinstance(instrument, VanillaInterestRateSwap):
            raise TypeError("DiscountingSwapEngine supports VanillaInterestRateSwap only")

        cashflow_engine = DiscountingCashflowEngine(self.discount_curve)
        floating_leg_pv = cashflow_engine.present_value(instrument.floating_leg())
        return floating_leg_pv / self.fixed_leg_annuity(instrument)
