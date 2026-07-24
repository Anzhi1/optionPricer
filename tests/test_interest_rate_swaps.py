from datetime import date
from math import exp

import pytest

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    DiscountingCashflowEngine,
    DiscountingSwapEngine,
    FixedRateCoupon,
    FlatForwardRateCurve,
    FlatYieldCurve,
    FloatingRateCoupon,
    Frequency,
    IborIndex,
    NullCalendar,
    SwapType,
    VanillaInterestRateSwap,
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


def make_swap(swap_type: SwapType = SwapType.PAYER) -> VanillaInterestRateSwap:
    return VanillaInterestRateSwap(
        swap_type=swap_type,
        notional=1_000_000.0,
        fixed_rate=0.05,
        fixed_schedule=make_annual_schedule(),
        fixed_day_count=Actual365Fixed(),
        floating_schedule=make_annual_schedule(),
        index=make_index(),
        spread=0.001,
    )


def test_vanilla_swap_generates_fixed_and_floating_legs() -> None:
    swap = make_swap()

    fixed_leg = swap.fixed_leg()
    floating_leg = swap.floating_leg()

    assert len(fixed_leg) == 2
    assert isinstance(fixed_leg[0], FixedRateCoupon)
    assert fixed_leg[0].amount() == pytest.approx(50_000.0)
    assert len(floating_leg) == 2
    assert isinstance(floating_leg[0], FloatingRateCoupon)
    assert floating_leg[0].rate() == pytest.approx(0.041)
    assert floating_leg[0].amount() == pytest.approx(41_000.0)


def test_discounting_swap_engine_prices_payer_swap() -> None:
    swap = make_swap(SwapType.PAYER)
    discount_curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )

    result = DiscountingSwapEngine(discount_curve).calculate(swap)
    fixed_leg_pv = 50_000.0 * exp(-0.05) + 50_000.0 * exp(-0.10)
    floating_leg_pv = 41_000.0 * exp(-0.05) + 41_000.0 * exp(-0.10)

    assert result.value == pytest.approx(floating_leg_pv - fixed_leg_pv)
    assert result.diagnostics == {
        "fixed_leg_pv": pytest.approx(fixed_leg_pv),
        "floating_leg_pv": pytest.approx(floating_leg_pv),
    }


def test_discounting_swap_engine_prices_receiver_swap() -> None:
    swap = make_swap(SwapType.RECEIVER)
    discount_curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )

    result = DiscountingSwapEngine(discount_curve).calculate(swap)
    manual_fixed = DiscountingCashflowEngine(discount_curve).present_value(swap.fixed_leg())
    manual_float = DiscountingCashflowEngine(discount_curve).present_value(swap.floating_leg())

    assert result.value == pytest.approx(manual_fixed - manual_float)


def test_vanilla_swap_rejects_invalid_notional() -> None:
    with pytest.raises(ValueError, match="notional"):
        VanillaInterestRateSwap(
            swap_type=SwapType.PAYER,
            notional=0.0,
            fixed_rate=0.05,
            fixed_schedule=make_annual_schedule(),
            fixed_day_count=Actual365Fixed(),
            floating_schedule=make_annual_schedule(),
            index=make_index(),
        )


def test_discounting_swap_engine_rejects_unsupported_instrument() -> None:
    with pytest.raises(TypeError, match="VanillaInterestRateSwap"):
        DiscountingSwapEngine(FlatYieldCurve(rate=0.05)).calculate(object())  # type: ignore[arg-type]
