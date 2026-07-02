# Phase 0 Architecture Design

This document defines the first architecture baseline for OptionPricer.

The goal is not to reproduce QuantLib. The goal is to keep the best parts of its
domain separation while using a smaller, clearer, research-first design.

The concrete implementation scope for the first working version is defined in
`docs/phase-1-mvp-spec.md`.

The market data and term-structure scope for the second implementation phase is
defined in `docs/phase-2-market-data-spec.md`.

## Core Principles

### Explicit Data Flow

Objects should not silently update each other. A pricing result should be
produced by an explicit call:

```python
result = engine.calculate(option)
```

The engine should be constructed with the market data, process, or model it
needs:

```python
process = BlackScholesMertonProcess(
    spot=100.0,
    risk_free_rate=0.05,
    dividend_yield=0.00,
    volatility=0.20,
)

engine = AnalyticBlackScholesEngine(process)
result = engine.calculate(option)
```

### Product Semantics vs Pricing Algorithms

An instrument describes what the contract is. A pricing engine describes how to
value it.

The product should not contain methods such as `black_scholes_price` or
`monte_carlo_price`. Those belong to engines.

### Shallow Abstractions

The first version should use a small number of abstract base classes or
protocols. They exist to clarify contracts, not to build a large framework.

Good first-level abstractions:

- `Instrument`
- `Payoff`
- `Exercise`
- `PricingEngine`
- `StochasticProcess`
- `YieldTermStructure`
- `VolatilityTermStructure`

### Composition First

A vanilla option is composed from a payoff and an exercise rule:

```python
option = VanillaOption(
    payoff=PlainVanillaPayoff(OptionType.CALL, strike=100.0),
    exercise=EuropeanExercise(maturity=1.0),
)
```

This keeps product classes small and makes the financial meaning visible.

### Asset Class Differences Through Components

The top-level architecture should not be partitioned by asset class. Avoid an
early package layout such as:

```text
equity/
fx/
rates/
commodities/
```

That structure looks tidy at first, but it tends to duplicate concepts such as
options, payoffs, exercises, discounting, volatility, interpolation, Monte Carlo,
and results.

Instead, asset class differences should be expressed through concrete
instruments, market data, processes, models, and engines. The shared framework
stays stable while each asset class contributes the components it actually
needs.

Guiding rule:

> Do not split the framework by asset class at the top level. Express asset
> class behavior through instrument, market data, process/model, and engine
> composition.

## Initial Package Layout

```text
option_pricer/
  __init__.py

  instruments/
    __init__.py
    base.py
    vanilla_option.py
    fx_option.py
    commodity_option.py
    rates/
      __init__.py
      bonds.py
      swaps.py

  payoffs/
    __init__.py
    base.py
    vanilla.py

  exercise/
    __init__.py
    base.py
    european.py
    american.py

  market/
    __init__.py
    quotes.py
    assets.py
    currencies.py

  termstructures/
    __init__.py
    yield_curve.py
    volatility.py
    forward_curve.py

  processes/
    __init__.py
    black_scholes_merton.py
    garman_kohlhagen.py
    black76.py

  engines/
    __init__.py
    base.py
    analytic/
      __init__.py
      black_scholes.py
    trees/
      __init__.py
      binomial.py
    monte_carlo/
      __init__.py
      european_option.py

  results/
    __init__.py
    greeks.py
    pricing_result.py

  math/
    __init__.py
    distributions.py
    random.py
    time_grid.py

tests/
  test_black_scholes.py
  test_binomial.py
  test_monte_carlo.py
```

Some files in this layout are future-facing. Phase 1 should only implement the
vanilla option path needed for the MVP. The names are included here to keep the
first design compatible with foreign exchange, rates, and commodity extensions.

## Domain Objects

### Instrument

An `Instrument` represents a contract that can be priced by compatible engines.

For Phase 1, the only concrete instrument is:

- `VanillaOption`

Future instruments should live under the same `instruments` area rather than in
asset-class top-level packages.

Examples:

- `FxOption`
- `CommodityOption`
- `FixedRateBond`
- `FloatingRateNote`
- `VanillaSwap`
- `CapFloor`
- `Swaption`

### Payoff

A `Payoff` maps an underlying value to a cash amount.

For Phase 1:

- `PlainVanillaPayoff`
- `OptionType.CALL`
- `OptionType.PUT`

### Exercise

An `Exercise` describes when the holder can exercise.

For Phase 1:

- `EuropeanExercise(maturity: float)`
- `AmericanExercise(maturity: float)`

Time is represented in year fractions during Phase 1. Calendar dates and day
count conventions are deliberately deferred.

The deferral is intentional:

- Phase 1 uses year fractions only.
- Phase 1 American exercise means continuously exercisable from valuation time to
  maturity; deferred American exercise is out of scope.
- Phase 2 introduces the minimal date, day-count or basis, calendar, holiday,
  and business-day adjustment support needed by curves.
- Phase 4 expands those foundations into schedule generation and cashflow dates
  for rates products.

### Process

A process describes the stochastic dynamics used by an engine.

For Phase 1:

- `BlackScholesMertonProcess`

The first version may accept flat numeric inputs directly:

```python
BlackScholesMertonProcess(
    spot=100.0,
    risk_free_rate=0.05,
    dividend_yield=0.00,
    volatility=0.20,
)
```

Later phases can replace these with term structure objects without changing the
instrument classes.

Asset-class-specific processes can then be added without changing the general
engine contract:

- `BlackScholesMertonProcess` for equity-style spot dynamics.
- `GarmanKohlhagenProcess` for foreign exchange options.
- `Black76Process` for forward-based options.
- `CommodityBlackProcess` for commodities or precious metals where carry,
  lease rates, or forward curves matter.
- `HullWhiteProcess` or short-rate models for rates.

### Pricing Engine

A pricing engine calculates a result for a supported instrument.

Initial interface:

```python
class PricingEngine(Protocol):
    def calculate(self, instrument: Instrument) -> PricingResult:
        ...
```

Concrete Phase 1 engines:

- `AnalyticBlackScholesEngine`
- `BinomialTreeEngine`
- `EuropeanMonteCarloEngine`

Engines may be generic or asset-class-specific.

Generic examples:

- Tree engines for vanilla exercise structures.
- Monte Carlo engines for path-based payoffs.
- Finite-difference engines once the grid abstractions are mature.

Specific examples:

- `DiscountingBondEngine`
- `DiscountingSwapEngine`
- `BlackCapFloorEngine`
- `FxBlackScholesEngine`
- `HullWhiteSwaptionEngine`

### Pricing Result

Pricing should return a structured result instead of a raw float.

```python
@dataclass(frozen=True)
class Greeks:
    delta: float | None = None
    gamma: float | None = None
    vega: float | None = None
    theta: float | None = None
    rho: float | None = None


@dataclass(frozen=True)
class PricingResult:
    value: float
    greeks: Greeks | None = None
    diagnostics: dict[str, object] | None = None
```

Engines are not required to return every Greek. Missing values should be `None`.

## Asset Class Boundaries

The framework should distinguish asset classes semantically, but not by creating
isolated top-level code islands.

### Equity-Style Products

Equity-style options are naturally described by spot, funding, dividends or
borrow, and volatility.

```python
process = BlackScholesMertonProcess(
    spot=100.0,
    risk_free_rate=0.05,
    dividend_yield=0.02,
    volatility=0.20,
)
```

The first MVP starts here because it is the shortest path to a complete pricing
flow.

### Foreign Exchange

FX options need a currency pair and two yield curves: domestic and foreign. The
foreign curve plays the role that dividend yield plays in the
Black-Scholes-Merton setup.

```python
process = GarmanKohlhagenProcess(
    spot=7.20,
    domestic_rate=0.04,
    foreign_rate=0.02,
    volatility=0.12,
    pair=CurrencyPair("USD", "CNH"),
)
```

The product and process can be FX-specific, while payoff, exercise, results, and
many numerical utilities remain shared.

FX should arrive before interest-rate products in the roadmap. It is a natural
extension of the Phase 1 option architecture and requires less new infrastructure
than bonds, swaps, schedules, and cashflows.

### Commodities and Precious Metals

Commodity and precious-metal products often depend on forward curves, carry,
storage costs, convenience yield, or lease rates. Precious metals can also behave
like currency-like assets in some markets.

Possible future process shapes:

```python
process = Black76Process(
    forward=2300.0,
    discount_rate=0.04,
    volatility=0.18,
)
```

or:

```python
process = CommodityBlackProcess(
    spot=2300.0,
    discount_curve=usd_curve,
    carry_curve=gold_lease_curve,
    volatility=gold_volatility,
    commodity="XAU",
)
```

Phase 1 should not implement this, but the architecture should leave a natural
place for it.

### Interest Rates

Rates are structurally different from spot assets. The central objects are
curves, indexes, schedules, and cashflows rather than a single spot price.

Example future shape:

```python
swap = VanillaSwap(
    fixed_leg=fixed_leg,
    floating_leg=floating_leg,
)

engine = DiscountingSwapEngine(
    discount_curve=usd_ois_curve,
    projection_curve=usd_libor_curve,
)
```

Rates should introduce cashflow and schedule abstractions when they are needed,
not before.

For this reason, rates products should come after the minimal date, day-count,
calendar, business-day, and curve foundations are in place.

### Design Consequences

- `Payoff`, `Exercise`, `PricingResult`, and numerical utilities should remain
  reusable across asset classes.
- `Instrument` classes may be asset-class-specific when contract semantics
  differ.
- `Process` and `Model` classes are the primary location for asset-class market
  dynamics.
- `Engine` classes may be shared when the algorithm is genuinely shared, and
  specialized when product mechanics require it.
- Market data should evolve from flat numeric inputs into explicit curve,
  volatility, quote, currency, index, and asset descriptors.

## API Style

Preferred usage:

```python
from option_pricer import (
    AnalyticBlackScholesEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
    VanillaOption,
)

option = VanillaOption(
    payoff=PlainVanillaPayoff(OptionType.CALL, strike=100.0),
    exercise=EuropeanExercise(maturity=1.0),
)

process = BlackScholesMertonProcess(
    spot=100.0,
    risk_free_rate=0.05,
    dividend_yield=0.00,
    volatility=0.20,
)

engine = AnalyticBlackScholesEngine(process)
result = engine.calculate(option)

print(result.value)
print(result.greeks.delta)
```

## Reuse Strategy

Reuse should happen where it keeps domain code small and readable.

Financial reuse:

- Payoffs reused by analytic, tree, and Monte Carlo engines.
- Exercise definitions reused by tree and future finite-difference engines.
- Process definitions reused by analytic, tree, and Monte Carlo engines where
  appropriate.
- Result objects reused across all engines.

Numerical reuse:

- Normal CDF/PDF.
- Random number generation.
- Time grids.
- Discounting helpers.
- Interpolation in later phases.

Avoid creating a generic numerical framework before multiple concrete engines
prove the abstraction is useful.

## Phase 1 MVP Decisions

Use Python for the first implementation.

Reasons:

- Fast iteration for research.
- Strong scientific computing ecosystem.
- Easy comparison with notebooks and QuantLib-Python.
- Lower friction for numerical experiments.

Initial dependency policy:

- Standard library for core dataclasses and typing.
- `math` for analytic formulas.
- `numpy` for Monte Carlo and vectorized calculations.
- `pytest` for tests.

`scipy` should not be required for the first Black-Scholes implementation because
the normal CDF can be implemented with `math.erf`.

## Date, Calendar, and Basis Placement

Date and market-convention infrastructure is important, but it should not be part
of Phase 1.

Phase 1 should use explicit year fractions such as `maturity=1.0`. This keeps
the first implementation focused on the pricing architecture: instruments,
payoffs, exercises, processes, engines, and results.

Later phases should introduce convention support in layers:

- Phase 2: minimal date utilities, day-count or basis conventions, calendars,
  holidays, and business-day adjustment for curves and term structures.
- Phase 3: reuse those foundations for FX and commodity option examples where
  dates are helpful but schedules are still light.
- Phase 4: add schedule generation, fixing dates, payment dates, accrual
  periods, and cashflow conventions for bonds and swaps.

This keeps the library honest about real-market conventions without letting
calendar infrastructure dominate the first pricing milestone.

## Non-Goals

The first architecture will not include:

- Observer pattern.
- Handle or relinkable handle objects.
- Lazy evaluation.
- Global evaluation date.
- Full calendar and business-day adjustment system.
- Full day-count convention system.
- Production-grade market data containers.
- Deep class hierarchies.
- Automatic dependency graph recalculation.

These are deferred until there is a concrete need.

## Open Questions

- Should package imports expose most user-facing classes from `option_pricer`, or
  should examples import from submodules?
- Should the first Monte Carlo engine support antithetic variates immediately?
- Should Greeks for non-analytic engines be added through finite differences in
  the engine, or through a separate sensitivity utility?

These questions do not block Phase 1 implementation, but they should be resolved
before the first public API is treated as stable.
