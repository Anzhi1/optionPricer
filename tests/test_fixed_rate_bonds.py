from datetime import date
from math import exp

import pytest

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    DiscountingBondEngine,
    DiscountingCashflowEngine,
    FixedCashflow,
    FixedRateBond,
    FixedRateCoupon,
    FlatYieldCurve,
    Frequency,
    NullCalendar,
    generate_schedule,
)


def make_annual_schedule():
    return generate_schedule(
        start_date=date(2026, 1, 15),
        end_date=date(2028, 1, 15),
        frequency=Frequency.ANNUAL,
        calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
    )


def test_fixed_rate_bond_generates_coupons_and_principal() -> None:
    bond = FixedRateBond(
        notional=1_000_000.0,
        fixed_rate=0.05,
        schedule=make_annual_schedule(),
        day_count=Actual365Fixed(),
    )

    cashflows = bond.cashflows()

    assert len(cashflows) == 3
    assert isinstance(cashflows[0], FixedRateCoupon)
    assert cashflows[0].amount() == pytest.approx(50_000.0)
    assert isinstance(cashflows[1], FixedRateCoupon)
    assert cashflows[1].amount() == pytest.approx(50_000.0)
    assert isinstance(cashflows[2], FixedCashflow)
    assert cashflows[2].amount() == pytest.approx(1_000_000.0)
    assert cashflows[2].payment_date == date(2028, 1, 15)


def test_fixed_rate_bond_allows_zero_coupon_rate() -> None:
    bond = FixedRateBond(
        notional=1_000_000.0,
        fixed_rate=0.0,
        schedule=make_annual_schedule(),
        day_count=Actual365Fixed(),
    )

    cashflows = bond.cashflows()

    assert cashflows[0].amount() == 0.0
    assert cashflows[1].amount() == 0.0
    assert cashflows[2].amount() == 1_000_000.0


def test_fixed_rate_bond_rejects_invalid_notional() -> None:
    with pytest.raises(ValueError, match="notional"):
        FixedRateBond(
            notional=0.0,
            fixed_rate=0.05,
            schedule=make_annual_schedule(),
            day_count=Actual365Fixed(),
        )


def test_discounting_bond_engine_matches_manual_cashflow_pv() -> None:
    bond = FixedRateBond(
        notional=1_000_000.0,
        fixed_rate=0.05,
        schedule=make_annual_schedule(),
        day_count=Actual365Fixed(),
    )
    curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )

    result = DiscountingBondEngine(curve).calculate(bond)
    manual = 50_000.0 * exp(-0.05) + 1_050_000.0 * exp(-0.10)
    cashflow_pv = DiscountingCashflowEngine(curve).present_value(bond.cashflows())

    assert result.value == pytest.approx(manual)
    assert result.value == pytest.approx(cashflow_pv)


def test_discounting_bond_engine_rejects_unsupported_instrument() -> None:
    with pytest.raises(TypeError, match="FixedRateBond"):
        DiscountingBondEngine(FlatYieldCurve(rate=0.05)).calculate(object())  # type: ignore[arg-type]
