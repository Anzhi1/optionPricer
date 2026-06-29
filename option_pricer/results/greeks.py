from dataclasses import dataclass


@dataclass(frozen=True)
class Greeks:
    delta: float | None = None
    gamma: float | None = None
    vega: float | None = None
    theta: float | None = None
    rho: float | None = None
