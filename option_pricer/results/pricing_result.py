from dataclasses import dataclass
from math import isfinite

from option_pricer.results.greeks import Greeks


@dataclass(frozen=True)
class PricingResult:
    value: float
    greeks: Greeks | None = None
    diagnostics: dict[str, object] | None = None

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise ValueError("value must be finite")
