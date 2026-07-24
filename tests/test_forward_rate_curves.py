from datetime import date

import pytest

from option_pricer import (
    Actual365Fixed,
    FlatForwardRateCurve,
    ForwardRateCurve,
)


def test_flat_forward_rate_curve_returns_constant_rate() -> None:
    curve = FlatForwardRateCurve(rate=0.035)

    assert curve.forward_rate(1.0, 1.25) == 0.035


def test_forward_rate_curve_interpolates_by_period_end_time() -> None:
    curve = ForwardRateCurve(times=[1.0, 2.0, 3.0], forward_rates=[0.03, 0.04, 0.06])

    assert curve.forward_rate(1.0, 1.5) == pytest.approx(0.035)


def test_forward_rate_curve_supports_date_inputs() -> None:
    curve = ForwardRateCurve(
        times=[1.0, 2.0],
        forward_rates=[0.03, 0.05],
        reference_date=date(2026, 1, 15),
        day_count=Actual365Fixed(),
    )

    assert curve.forward_rate(date(2026, 7, 16), date(2027, 1, 15)) == pytest.approx(0.03)


def test_forward_rate_curve_allows_negative_rates() -> None:
    curve = ForwardRateCurve(times=[1.0, 2.0], forward_rates=[-0.005, 0.01])

    assert curve.forward_rate(0.5, 1.0) == pytest.approx(-0.005)


def test_forward_rate_curve_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="same length"):
        ForwardRateCurve(times=[1.0, 2.0], forward_rates=[0.03])
    with pytest.raises(ValueError, match="at least two"):
        ForwardRateCurve(times=[1.0], forward_rates=[0.03])
    with pytest.raises(ValueError, match="strictly increasing"):
        ForwardRateCurve(times=[1.0, 1.0], forward_rates=[0.03, 0.04])
    with pytest.raises(ValueError, match="finite"):
        ForwardRateCurve(times=[1.0, 2.0], forward_rates=[0.03, float("nan")])


def test_forward_rate_curve_rejects_invalid_period() -> None:
    curve = FlatForwardRateCurve(rate=0.035)

    with pytest.raises(ValueError, match="after start"):
        curve.forward_rate(1.0, 1.0)
    with pytest.raises(TypeError, match="both be dates"):
        curve.forward_rate(1.0, date(2027, 1, 15))
