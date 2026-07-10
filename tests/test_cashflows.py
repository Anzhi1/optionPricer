from datetime import date

import pytest

from option_pricer import Actual365Fixed, FixedCashflow, FixedRateCoupon


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
