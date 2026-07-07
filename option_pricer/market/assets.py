from dataclasses import dataclass


@dataclass(frozen=True)
class Commodity:
    """Lightweight commodity or precious-metal descriptor."""

    symbol: str
    name: str | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str):
            raise TypeError("commodity symbol must be a string")
        normalized = self.symbol.upper()
        if not normalized:
            raise ValueError("commodity symbol must not be empty")
        object.__setattr__(self, "symbol", normalized)
