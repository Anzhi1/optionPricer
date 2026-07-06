# Phase 3 FX and Commodity Specification

This document defines the first extension beyond equity-style vanilla options.

Phase 3 should test whether the architecture can support foreign exchange and
commodity-style options through components, without creating isolated top-level
asset-class packages.

## Goals

- Add lightweight currency and currency-pair descriptors.
- Add a Garman-Kohlhagen process for FX options.
- Reuse vanilla payoffs, European exercise, results, and analytic pricing where
  the financial model is the same Black-style formula.
- Keep FX market data explicit: spot, domestic curve, foreign curve, and Black
  volatility.
- Leave commodity and precious-metal conventions as a near-term design target,
  not a large implementation in the first Phase 3 step.

## Non-Goals

- Full FX convention databases.
- Cross-currency curve construction.
- FX delta convention variants.
- Premium-adjusted Greeks.
- Volatility smiles, surfaces, or deltas.
- Commodity storage, delivery, or lease-rate modeling.
- A top-level `fx` package that duplicates shared option infrastructure.

## Package Additions

```text
option_pricer/
  market/
    currencies.py

  instruments/
    fx_option.py

  processes/
    garman_kohlhagen.py
```

## Currency

Location: `option_pricer.market.currencies`

Fields:

- `code: str`
- `name: str | None = None`

Validation:

- Code must be a three-letter alphabetic ISO-style code.
- Code is normalized to uppercase.

The class is deliberately descriptive only. It should not contain calendars,
settlement rules, or market conventions in Phase 3.

## CurrencyPair

Fields:

- `base: Currency`
- `quote: Currency`

Meaning:

- Spot is expressed as quote currency units per one base currency unit.
- `EUR/USD = 1.10` means one EUR is worth 1.10 USD.

Convenience:

- `symbol` returns `"EUR/USD"`.
- `inverse()` returns the opposite pair.

## Garman-Kohlhagen Process

Location: `option_pricer.processes.garman_kohlhagen`

Fields:

- `spot: float`
- `domestic_rate: float`
- `foreign_rate: float`
- `volatility: float`
- `pair: CurrencyPair | None = None`

Validation:

- `spot > 0`
- `volatility > 0`

Rates may be negative.

Behavior:

- Domestic discount factor: `exp(-domestic_rate * t)`
- Foreign discount factor: `exp(-foreign_rate * t)`
- Forward: `spot * exp((domestic_rate - foreign_rate) * t)`

The process should expose `risk_free_rate` and `dividend_yield` compatibility
properties so the existing analytic Black-Scholes engine can price European
vanilla FX options without duplicating formulas.

## Term-Structure Constructor

The process should support snapshot construction:

```python
process = GarmanKohlhagenProcess.from_term_structures(
    spot=SimpleQuote(1.10),
    maturity=1.0,
    domestic_curve=usd_curve,
    foreign_curve=eur_curve,
    volatility=eurusd_vol,
    pair=CurrencyPair(Currency("EUR"), Currency("USD")),
)
```

Updating the quote or curves later should not mutate the process.

## FX Vanilla Option

Location: `option_pricer.instruments.fx_option`

`FxVanillaOption` should add FX contract semantics while reusing the existing
plain vanilla payoff and exercise abstractions.

Fields:

- `pair: CurrencyPair`
- `payoff: PlainVanillaPayoff`
- `exercise: Exercise`
- `notional: float = 1.0`

Conventions:

- Spot and strike are quote currency units per one base currency unit.
- Engine values are quote currency units per one base notional.
- Notional is a base-currency amount and is used only through explicit scaling.
- `notional_value(unit_value)` converts a per-base-notional value to a quote
  currency amount.

The analytic Black-style engine can support this instrument by extracting the
same payoff and maturity data used for the generic `VanillaOption`.

## First Exit Criteria

- `Currency` and `CurrencyPair` are tested.
- `FxVanillaOption` is tested.
- `GarmanKohlhagenProcess` helpers are tested.
- Term-structure construction works with existing yield and volatility curves.
- Existing `AnalyticBlackScholesEngine` can price a European FX vanilla option.
- A runnable FX example demonstrates the intended API.
