from datetime import date
from math import exp, log

import pytest

from option_pricer import Actual365Fixed, DiscountCurve, FlatYieldCurve, ZeroCurve


def test_flat_yield_curve_discount_and_zero_rate_with_time_input() -> None:
    curve = FlatYieldCurve(rate=0.05)

    assert curve.discount(1.0) == pytest.approx(exp(-0.05))
    assert curve.zero_rate(5.0) == 0.05


def test_flat_yield_curve_supports_date_input() -> None:
    curve = FlatYieldCurve(
        rate=0.05,
        reference_date=date(2026, 7, 2),
        day_count=Actual365Fixed(),
    )

    assert curve.discount(date(2027, 7, 2)) == pytest.approx(exp(-0.05))
    assert curve.zero_rate(date(2027, 7, 2)) == 0.05


def test_flat_yield_curve_requires_complete_date_configuration() -> None:
    with pytest.raises(ValueError, match="provided together"):
        FlatYieldCurve(rate=0.05, reference_date=date(2026, 7, 2))


def test_date_maturity_requires_reference_date_and_day_count() -> None:
    curve = FlatYieldCurve(rate=0.05)

    with pytest.raises(ValueError, match="date maturity"):
        curve.discount(date(2027, 7, 2))


def test_yield_curve_rejects_negative_or_non_finite_maturity() -> None:
    curve = FlatYieldCurve(rate=0.05)

    with pytest.raises(ValueError, match="non-negative"):
        curve.discount(-1.0)
    with pytest.raises(ValueError, match="finite"):
        curve.discount(float("nan"))


def test_zero_curve_interpolates_zero_rates() -> None:
    curve = ZeroCurve(times=[1.0, 2.0, 3.0], zero_rates=[0.03, 0.04, 0.06])

    assert curve.zero_rate(1.5) == pytest.approx(0.035)
    assert curve.discount(1.5) == pytest.approx(exp(-0.035 * 1.5))


def test_zero_curve_supports_date_input() -> None:
    curve = ZeroCurve(
        times=[1.0, 2.0],
        zero_rates=[0.03, 0.05],
        reference_date=date(2026, 7, 2),
        day_count=Actual365Fixed(),
    )

    assert curve.zero_rate(date(2027, 7, 2)) == pytest.approx(0.03)


def test_zero_curve_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="same length"):
        ZeroCurve(times=[1.0, 2.0], zero_rates=[0.03])
    with pytest.raises(ValueError, match="at least two"):
        ZeroCurve(times=[1.0], zero_rates=[0.03])
    with pytest.raises(ValueError, match="positive"):
        ZeroCurve(times=[0.0, 1.0], zero_rates=[0.03, 0.04])
    with pytest.raises(ValueError, match="strictly increasing"):
        ZeroCurve(times=[1.0, 1.0], zero_rates=[0.03, 0.04])
    with pytest.raises(ValueError, match="finite"):
        ZeroCurve(times=[1.0, 2.0], zero_rates=[0.03, float("nan")])


def test_zero_curve_rejects_extrapolation() -> None:
    curve = ZeroCurve(times=[1.0, 2.0], zero_rates=[0.03, 0.04])

    with pytest.raises(ValueError, match="outside"):
        curve.zero_rate(0.5)
    with pytest.raises(ValueError, match="outside"):
        curve.discount(3.0)


def test_discount_curve_uses_log_discount_interpolation() -> None:
    d1 = exp(-0.03 * 1.0)
    d2 = exp(-0.05 * 2.0)
    curve = DiscountCurve(times=[1.0, 2.0], discount_factors=[d1, d2])

    expected_log_discount = 0.5 * (log(d1) + log(d2))
    assert curve.discount(1.5) == pytest.approx(exp(expected_log_discount))
    assert curve.zero_rate(1.5) == pytest.approx(-expected_log_discount / 1.5)


def test_discount_curve_rejects_invalid_discount_factors() -> None:
    with pytest.raises(ValueError, match="positive"):
        DiscountCurve(times=[1.0, 2.0], discount_factors=[0.95, 0.0])
    with pytest.raises(ValueError, match="finite"):
        DiscountCurve(times=[1.0, 2.0], discount_factors=[0.95, float("inf")])


def test_discount_curve_zero_rate_is_undefined_at_time_zero() -> None:
    curve = DiscountCurve(times=[1.0, 2.0], discount_factors=[0.95, 0.90])

    with pytest.raises(ValueError, match="time zero"):
        curve.zero_rate(0.0)
