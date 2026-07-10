from datetime import date
from math import exp

import pytest

from option_pricer import (
    Actual365Fixed,
    DiscountingCashflowEngine,
    FixedCashflow,
    FixedRateCoupon,
    FlatYieldCurve,
)


def test_discounting_single_cashflow_present_value() -> None:
    curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )
    engine = DiscountingCashflowEngine(curve)

    value = engine.present_value([FixedCashflow(payment_date=date(2027, 1, 15), value=1_000.0)])

    assert value == pytest.approx(1_000.0 * exp(-0.05))


def test_discounting_multiple_cashflows_present_value() -> None:
    curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )
    cashflows = [
        FixedRateCoupon(
            accrual_start=date(2026, 1, 15),
            accrual_end=date(2027, 1, 15),
            payment_date=date(2027, 1, 15),
            notional=1_000_000.0,
            fixed_rate=0.05,
            day_count=Actual365Fixed(),
        ),
        FixedCashflow(payment_date=date(2027, 1, 15), value=1_000_000.0),
    ]

    value = DiscountingCashflowEngine(curve).present_value(cashflows)

    assert value == pytest.approx(1_050_000.0 * exp(-0.05))


def test_discounting_rejects_past_cashflow_through_curve() -> None:
    curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )
    cashflow = FixedCashflow(payment_date=date(2025, 1, 15), value=1_000.0)

    with pytest.raises(ValueError, match="end date"):
        DiscountingCashflowEngine(curve).present_value([cashflow])


def test_discounting_empty_cashflow_sequence_is_zero() -> None:
    curve = FlatYieldCurve(rate=0.05)

    assert DiscountingCashflowEngine(curve).present_value([]) == 0.0
