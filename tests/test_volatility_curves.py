from datetime import date

import pytest

from option_pricer import Actual365Fixed, BlackVolCurve, FlatVolatility


def test_flat_volatility_returns_constant_volatility() -> None:
    vol = FlatVolatility(0.20)

    assert vol.black_vol(1.0) == 0.20
    assert vol.black_vol(10.0, strike=100.0) == 0.20


def test_flat_volatility_supports_date_input() -> None:
    vol = FlatVolatility(
        0.20,
        reference_date=date(2026, 7, 3),
        day_count=Actual365Fixed(),
    )

    assert vol.black_vol(date(2027, 7, 3)) == 0.20


def test_flat_volatility_requires_complete_date_configuration() -> None:
    with pytest.raises(ValueError, match="provided together"):
        FlatVolatility(0.20, reference_date=date(2026, 7, 3))


def test_flat_volatility_rejects_invalid_volatility() -> None:
    with pytest.raises(ValueError, match="positive"):
        FlatVolatility(0.0)
    with pytest.raises(ValueError, match="finite"):
        FlatVolatility(float("nan"))


def test_black_vol_curve_interpolates_volatility() -> None:
    curve = BlackVolCurve(times=[1.0, 2.0, 3.0], volatilities=[0.20, 0.25, 0.35])

    assert curve.black_vol(1.5) == pytest.approx(0.225)
    assert curve.black_vol(2.5, strike=100.0) == pytest.approx(0.30)


def test_black_vol_curve_supports_date_input() -> None:
    curve = BlackVolCurve(
        times=[1.0, 2.0],
        volatilities=[0.20, 0.30],
        reference_date=date(2026, 7, 3),
        day_count=Actual365Fixed(),
    )

    assert curve.black_vol(date(2027, 7, 3)) == pytest.approx(0.20)


def test_black_vol_curve_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="same length"):
        BlackVolCurve(times=[1.0, 2.0], volatilities=[0.20])
    with pytest.raises(ValueError, match="at least two"):
        BlackVolCurve(times=[1.0], volatilities=[0.20])
    with pytest.raises(ValueError, match="positive"):
        BlackVolCurve(times=[0.0, 1.0], volatilities=[0.20, 0.25])
    with pytest.raises(ValueError, match="strictly increasing"):
        BlackVolCurve(times=[1.0, 1.0], volatilities=[0.20, 0.25])
    with pytest.raises(ValueError, match="finite"):
        BlackVolCurve(times=[1.0, 2.0], volatilities=[0.20, float("inf")])


def test_black_vol_curve_rejects_extrapolation() -> None:
    curve = BlackVolCurve(times=[1.0, 2.0], volatilities=[0.20, 0.25])

    with pytest.raises(ValueError, match="outside"):
        curve.black_vol(0.5)
    with pytest.raises(ValueError, match="outside"):
        curve.black_vol(3.0)


def test_date_maturity_requires_reference_date_and_day_count() -> None:
    curve = BlackVolCurve(times=[1.0, 2.0], volatilities=[0.20, 0.25])

    with pytest.raises(ValueError, match="date maturity"):
        curve.black_vol(date(2027, 7, 3))
