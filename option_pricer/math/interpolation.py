from collections.abc import Sequence


def linear_interpolate(x: float, xs: Sequence[float], ys: Sequence[float]) -> float:
    """Linearly interpolate y at x without extrapolation."""

    _validate_points(xs, ys)

    if x < xs[0] or x > xs[-1]:
        raise ValueError("x is outside the interpolation range")

    if x == xs[0]:
        return float(ys[0])
    if x == xs[-1]:
        return float(ys[-1])

    for index in range(1, len(xs)):
        left_x = xs[index - 1]
        right_x = xs[index]
        if x <= right_x:
            left_y = ys[index - 1]
            right_y = ys[index]
            weight = (x - left_x) / (right_x - left_x)
            return float(left_y + weight * (right_y - left_y))

    raise RuntimeError("unreachable interpolation state")


def _validate_points(xs: Sequence[float], ys: Sequence[float]) -> None:
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")
    if len(xs) < 2:
        raise ValueError("at least two interpolation points are required")
    if any(xs[index] <= xs[index - 1] for index in range(1, len(xs))):
        raise ValueError("xs must be strictly increasing")
