from collections.abc import Sequence
from dataclasses import dataclass

from option_pricer.cashflows.cashflow import Cashflow
from option_pricer.termstructures.yield_curve import YieldTermStructure


@dataclass(frozen=True)
class DiscountingCashflowEngine:
    """Discount dated cashflows with a yield term structure."""

    discount_curve: YieldTermStructure

    def present_value(self, cashflows: Sequence[Cashflow]) -> float:
        return sum(
            cashflow.amount() * self.discount_curve.discount(cashflow.payment_date)
            for cashflow in cashflows
        )
