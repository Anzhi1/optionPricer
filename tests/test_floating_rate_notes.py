from datetime import date
from math import exp

import pytest

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    DiscountingBondEngine,
    DiscountingCashflowEngine,
    FixedCashflow,
    FlatForwardRateCurve,
    FlatYieldCurve,
    FloatingRateCoupon,
    FloatingRateNote,
    Frequency,
    IborIndex,
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


def make_index() -> IborIndex:
    day_count = Actual365Fixed()
    projection_curve = FlatForwardRateCurve(
        rate=0.04,
        reference_date=date(2026, 1, 15),
        day_count=day_count,
    )
    return IborIndex(
        name="USD-TEST-12M",
        tenor_months=12,
        day_count=day_count,
        fixing_calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
        projection_curve=projection_curve,
    )


def test_floating_rate_note_generates_coupons_and_principal() -> None:
    note = FloatingRateNote(
        notional=1_000_000.0,
        spread=0.001,
        schedule=make_annual_schedule(),
        index=make_index(),
    )

    cashflows = note.cashflows()

    assert len(cashflows) == 3
    assert isinstance(cashflows[0], FloatingRateCoupon)
    assert cashflows[0].rate() == pytest.approx(0.041)
    assert cashflows[0].amount() == pytest.approx(41_000.0)
    assert isinstance(cashflows[1], FloatingRateCoupon)
    assert cashflows[1].amount() == pytest.approx(41_000.0)
    assert isinstance(cashflows[2], FixedCashflow)
    assert cashflows[2].amount() == pytest.approx(1_000_000.0)


def test_floating_rate_note_rejects_invalid_notional() -> None:
    with pytest.raises(ValueError, match="notional"):
        FloatingRateNote(
            notional=0.0,
            spread=0.001,
            schedule=make_annual_schedule(),
            index=make_index(),
        )


def test_discounting_bond_engine_prices_floating_rate_note() -> None:
    note = FloatingRateNote(
        notional=1_000_000.0,
        spread=0.001,
        schedule=make_annual_schedule(),
        index=make_index(),
    )
    discount_curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )

    result = DiscountingBondEngine(discount_curve).calculate(note)
    manual = 41_000.0 * exp(-0.05) + 1_041_000.0 * exp(-0.10)
    cashflow_pv = DiscountingCashflowEngine(discount_curve).present_value(note.cashflows())

    assert result.value == pytest.approx(manual)
    assert result.value == pytest.approx(cashflow_pv)
