from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    """Lightweight ISO-style currency descriptor."""

    code: str
    name: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.code, str):
            raise TypeError("currency code must be a string")
        normalized = self.code.upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency code must be a three-letter alphabetic code")
        object.__setattr__(self, "code", normalized)


@dataclass(frozen=True)
class CurrencyPair:
    """Currency pair quoted as quote currency units per one base currency unit."""

    base: Currency
    quote: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.base, Currency):
            raise TypeError("base must be a Currency")
        if not isinstance(self.quote, Currency):
            raise TypeError("quote must be a Currency")
        if self.base == self.quote:
            raise ValueError("base and quote currencies must differ")

    @property
    def symbol(self) -> str:
        return f"{self.base.code}/{self.quote.code}"

    def inverse(self) -> "CurrencyPair":
        return CurrencyPair(base=self.quote, quote=self.base)

