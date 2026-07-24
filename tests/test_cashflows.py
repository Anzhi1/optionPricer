from datetime import date

import pytest

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    FixedCashflow,
    FixedRateCoupon,
    FlatForwardRateCurve,
    FloatingRateCoupon,
    Frequency,
    IborIndex,
    NullCalendar,
    WeekendCalendar,
    fixed_rate_leg,
    floating_rate_leg,
    generate_schedule,
)


def test_fixed_cashflow_amount() -> None:
    cashflow = FixedCashflow(payment_date=date(2027, 1, 15), value=1_000.0)

    assert cashflow.amount() == 1_000.0


def test_fixed_cashflow_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="finite"):
        FixedCashflow(payment_date=date(2027, 1, 15), value=float("nan"))


def test_fixed_rate_coupon_amount() -> None:
    coupon = FixedRateCoupon(
        accrual_start=date(2026, 1, 15),
        accrual_end=date(2027, 1, 15),
        payment_date=date(2027, 1, 15),
        notional=1_000_000.0,
        fixed_rate=0.05,
        day_count=Actual365Fixed(),
    )

    assert coupon.amount() == pytest.approx(50_000.0)


def test_fixed_rate_coupon_allows_negative_fixed_rate() -> None:
    coupon = FixedRateCoupon(
        accrual_start=date(2026, 1, 15),
        accrual_end=date(2027, 1, 15),
        payment_date=date(2027, 1, 15),
        notional=1_000_000.0,
        fixed_rate=-0.01,
        day_count=Actual365Fixed(),
    )

    assert coupon.amount() == pytest.approx(-10_000.0)


def test_fixed_rate_coupon_rejects_invalid_notional() -> None:
    with pytest.raises(ValueError, match="notional"):
        FixedRateCoupon(
            accrual_start=date(2026, 1, 15),
            accrual_end=date(2027, 1, 15),
            payment_date=date(2027, 1, 15),
            notional=0.0,
            fixed_rate=0.05,
            day_count=Actual365Fixed(),
        )


def test_fixed_rate_coupon_rejects_invalid_accrual_dates() -> None:
    with pytest.raises(ValueError, match="accrual_end"):
        FixedRateCoupon(
            accrual_start=date(2027, 1, 15),
            accrual_end=date(2026, 1, 15),
            payment_date=date(2027, 1, 15),
            notional=1_000_000.0,
            fixed_rate=0.05,
            day_count=Actual365Fixed(),
        )


def test_floating_rate_coupon_projects_rate_and_amount() -> None:
    day_count = Actual365Fixed()
    curve = FlatForwardRateCurve(
        rate=0.05,
        reference_date=date(2026, 1, 15),
        day_count=day_count,
    )
    index = IborIndex(
        name="USD-TEST-12M",
        tenor_months=12,
        day_count=day_count,
        fixing_calendar=WeekendCalendar(),
        business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
        projection_curve=curve,
    )
    coupon = FloatingRateCoupon(
        accrual_start=date(2027, 1, 15),
        accrual_end=date(2028, 1, 15),
        payment_date=date(2028, 1, 15),
        notional=1_000_000.0,
        spread=0.001,
        day_count=day_count,
        index=index,
    )
    expected_rate = 0.051

    assert coupon.rate() == pytest.approx(expected_rate)
    assert coupon.amount() == pytest.approx(1_000_000.0 * expected_rate)


def test_floating_rate_coupon_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="notional"):
        FloatingRateCoupon(
            accrual_start=date(2026, 1, 15),
            accrual_end=date(2027, 1, 15),
            payment_date=date(2027, 1, 15),
            notional=0.0,
            spread=0.001,
            day_count=Actual365Fixed(),
            index=IborIndex(
                name="USD-TEST-12M",
                tenor_months=12,
                day_count=Actual365Fixed(),
                fixing_calendar=WeekendCalendar(),
                business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
                projection_curve=FlatForwardRateCurve(rate=0.05),
            ),
        )


def test_fixed_rate_leg_builds_coupons_from_schedule() -> None:
    schedule = generate_schedule(
        start_date=date(2026, 1, 15),
        end_date=date(2028, 1, 15),
        frequency=Frequency.ANNUAL,
        calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
    )

    leg = fixed_rate_leg(
        schedule=schedule,
        notional=1_000_000.0,
        fixed_rate=0.05,
        day_count=Actual365Fixed(),
    )

    assert len(leg) == 2
    assert isinstance(leg[0], FixedRateCoupon)
    assert leg[0].amount() == pytest.approx(50_000.0)
    assert leg[1].amount() == pytest.approx(50_000.0)


def test_floating_rate_leg_builds_coupons_from_schedule() -> None:
    day_count = Actual365Fixed()
    schedule = generate_schedule(
        start_date=date(2026, 1, 15),
        end_date=date(2028, 1, 15),
        frequency=Frequency.ANNUAL,
        calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
    )
    index = IborIndex(
        name="USD-TEST-12M",
        tenor_months=12,
        day_count=day_count,
        fixing_calendar=NullCalendar(),
        business_day_convention=BusinessDayConvention.UNADJUSTED,
        projection_curve=FlatForwardRateCurve(
            rate=0.04,
            reference_date=date(2026, 1, 15),
            day_count=day_count,
        ),
    )

    leg = floating_rate_leg(
        schedule=schedule,
        notional=1_000_000.0,
        spread=0.001,
        index=index,
    )

    assert len(leg) == 2
    assert isinstance(leg[0], FloatingRateCoupon)
    assert leg[0].rate() == pytest.approx(0.041)
    assert leg[0].amount() == pytest.approx(41_000.0)
    assert leg[1].amount() == pytest.approx(41_000.0)
