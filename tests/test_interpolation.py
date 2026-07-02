import pytest

from option_pricer import linear_interpolate


def test_linear_interpolate_at_endpoints() -> None:
    xs = [1.0, 2.0, 3.0]
    ys = [10.0, 20.0, 40.0]

    assert linear_interpolate(1.0, xs, ys) == 10.0
    assert linear_interpolate(3.0, xs, ys) == 40.0


def test_linear_interpolate_inside_interval() -> None:
    xs = [1.0, 2.0, 3.0]
    ys = [10.0, 20.0, 40.0]

    assert linear_interpolate(1.5, xs, ys) == pytest.approx(15.0)
    assert linear_interpolate(2.5, xs, ys) == pytest.approx(30.0)


def test_linear_interpolate_rejects_extrapolation() -> None:
    xs = [1.0, 2.0]
    ys = [10.0, 20.0]

    with pytest.raises(ValueError, match="outside"):
        linear_interpolate(0.5, xs, ys)
    with pytest.raises(ValueError, match="outside"):
        linear_interpolate(2.5, xs, ys)


def test_linear_interpolate_requires_matching_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        linear_interpolate(1.0, [1.0, 2.0], [10.0])


def test_linear_interpolate_requires_at_least_two_points() -> None:
    with pytest.raises(ValueError, match="at least two"):
        linear_interpolate(1.0, [1.0], [10.0])


def test_linear_interpolate_requires_strictly_increasing_xs() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        linear_interpolate(1.0, [1.0, 1.0], [10.0, 20.0])
    with pytest.raises(ValueError, match="strictly increasing"):
        linear_interpolate(1.0, [2.0, 1.0], [20.0, 10.0])
