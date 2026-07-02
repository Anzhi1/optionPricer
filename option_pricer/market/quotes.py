from dataclasses import dataclass
from math import isfinite


@dataclass
class SimpleQuote:
    """Mutable quote updated explicitly by assigning to value."""

    _value: float

    def __init__(self, value: float) -> None:
        self.value = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        if not isfinite(value):
            raise ValueError("quote value must be finite")
        self._value = float(value)
