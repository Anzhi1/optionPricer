from datetime import date

import pytest

from option_pricer import Actual365Fixed, FlatForwardCurve, ForwardCurve


def test_flat_forward_curve_returns_constant_forward() -> None:
    curve = FlatForwardCurve(forward_value=100.0)

    assert curve.forward(0.5) == 100.0
    assert curve.forward(2.0) == 100.0


def test_flat_forward_curve_accepts_date_maturity() -> None:
    curve = FlatForwardCurve(
        forward_value=100.0,
        reference_date=date(2026, 7, 2),
        day_count=Actual365Fixed(),
    )

    assert curve.forward(date(2027, 7, 2)) == 100.0


def test_forward_curve_interpolates_forwards() -> None:
    curve = ForwardCurve(times=[1.0, 2.0, 3.0], forwards=[100.0, 110.0, 130.0])

    assert curve.forward(1.5) == pytest.approx(105.0)
    assert curve.forward(2.5) == pytest.approx(120.0)


def test_forward_curve_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="same length"):
        ForwardCurve(times=[1.0, 2.0], forwards=[100.0])

    with pytest.raises(ValueError, match="positive"):
        ForwardCurve(times=[1.0, 2.0], forwards=[100.0, 0.0])

    with pytest.raises(ValueError, match="strictly increasing"):
        ForwardCurve(times=[1.0, 1.0], forwards=[100.0, 101.0])
