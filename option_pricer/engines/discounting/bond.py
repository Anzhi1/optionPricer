from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from option_pricer.cashflows.cashflow import Cashflow
from option_pricer.engines.discounting.cashflows import DiscountingCashflowEngine
from option_pricer.results.pricing_result import PricingResult
from option_pricer.termstructures.yield_curve import YieldTermStructure


@runtime_checkable
class CashflowInstrument(Protocol):
    """Instrument that can expose dated cashflows."""

    def cashflows(self) -> tuple[Cashflow, ...]:
        ...


@dataclass(frozen=True)
class DiscountingBondEngine:
    """Discounting engine for bond-like cashflow instruments."""

    discount_curve: YieldTermStructure

    def calculate(self, instrument: CashflowInstrument) -> PricingResult:
        if not isinstance(instrument, CashflowInstrument):
            raise TypeError("DiscountingBondEngine supports instruments with cashflows")
        value = DiscountingCashflowEngine(self.discount_curve).present_value(instrument.cashflows())
        return PricingResult(value=value)
