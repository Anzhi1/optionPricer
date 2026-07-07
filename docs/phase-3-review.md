# Phase 3 Review Notes

This review summarizes the first FX and commodity implementation pass.

## What Is In Good Shape

- Asset-class differences are expressed through components rather than top-level
  package silos.
- FX contract semantics live in `FxVanillaOption`; FX dynamics live in
  `GarmanKohlhagenProcess`.
- Commodity contract semantics live in `CommodityVanillaOption`; forward-style
  dynamics live in `Black76Process`.
- `BlackStyleProcess` captures only the repeated lognormal Black-style behavior:
  underlying value, volatility, discount rate, underlying growth rate, discount
  factor, and underlying discount factor.
- Analytic, terminal Monte Carlo, and CRR tree engines reuse that interface where
  the model assumptions genuinely match.
- Market data remains explicit and snapshot-based. Quotes can update, but
  dependent processes do not silently recalculate.

## Boundaries To Preserve

- `BlackStyleProcess` is not a general stochastic-process interface.
- `EuropeanMonteCarloEngine` is not a general path simulation framework.
- `BinomialTreeEngine` is not a general lattice framework.
- `ForwardCurve` is a forward price curve, not a bootstrapped commodity curve.
- `CommodityVanillaOption` does not model storage, delivery, location, lease
  rates, or futures margining.

## Known Deferred Topics

- FX delta conventions.
- FX volatility smile/surface construction.
- ATM, risk-reversal, and butterfly quote conversion.
- Premium-adjusted Greeks.
- Commodity delivery and storage economics.
- General-purpose Monte Carlo, tree, and finite-difference engines for models
  such as Heston, local volatility, Hull-White, or other short-rate models.

## Design Watchlist

- `AnalyticBlackScholesEngine` currently imports each supported vanilla-style
  instrument class. This is still acceptable at Phase 3 size, but if more
  vanilla-style instruments appear, introduce a small shared instrument protocol
  for `payoff` and `exercise` rather than growing the union indefinitely.
- `FxVanillaOption` and `CommodityVanillaOption` intentionally duplicate a small
  amount of validation. A shared helper may become worthwhile if a third
  asset-specific vanilla option repeats the same pattern.
- `GarmanKohlhagenProcess` still exposes `risk_free_rate` and `dividend_yield`
  compatibility properties. New Black-style engine code should prefer
  `discount_rate` and `underlying_growth_rate`.

## Recommended Next Step

Before starting Phase 4 rates products, push the local commits when GitHub
network access is available. Then begin Phase 4 with schedule and cashflow
design, not with swaps directly.
