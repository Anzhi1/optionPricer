# OptionPricer

OptionPricer is a QuantLib-inspired pricing and valuation library for learning,
research, and transparent financial engineering experiments.

The first milestone focuses on a small vanilla option pricing stack:

- explicit instruments, payoffs, exercises, processes, and engines,
- no observer, handle, lazy-evaluation, or global evaluation-date machinery,
- year-fraction based inputs before calendars and day-count conventions are
  introduced in later phases.

## Development Setup

This project uses `uv` for dependency and virtual-environment management.

On this Windows environment, `uv` is available through Python:

```powershell
py -m uv sync --extra dev
py -m uv run pytest
```

If `uv` is on your PATH, the shorter commands also work:

```powershell
uv sync --extra dev
uv run pytest
```

`uv.lock` should be committed so dependency resolution is reproducible. The
local `.venv/` directory should not be committed.

## Project Layout

```text
option_pricer/
  instruments/   contract definitions, such as VanillaOption
  payoffs/       payoff functions, such as PlainVanillaPayoff
  exercise/      exercise rules, such as EuropeanExercise and AmericanExercise
  processes/     market dynamics, such as BlackScholesMertonProcess
  engines/       pricing algorithms, such as analytic, tree, and Monte Carlo
  results/       PricingResult and Greeks
  time/          day counters, calendars, and business-day adjustment
  math/          small numerical helpers

tests/           pytest test suite
examples/        runnable usage examples
docs/            roadmap and architecture notes
```

The package is organized around financial concepts instead of asset-class
silos. New products should compose reusable payoffs, exercises, processes, and
engines where that keeps the financial logic visible.

## Minimal Example

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
    dividend_yield=0.0,
    volatility=0.20,
)

engine = AnalyticBlackScholesEngine(process)
result = engine.calculate(option)

print(result.value)
print(result.greeks.delta)
```

## Examples

Run examples through `uv` so they use the project environment:

```powershell
py -m uv run python examples/analytic_black_scholes.py
py -m uv run python examples/binomial_european_american.py
py -m uv run python examples/monte_carlo_vs_analytic.py
```

The examples are intentionally small. They are meant to show how the core
objects fit together:

- `VanillaOption` describes the contract.
- `PlainVanillaPayoff` describes call or put payoff.
- `EuropeanExercise` and `AmericanExercise` describe exercise rights.
- `BlackScholesMertonProcess` holds flat market assumptions.
- Engines implement pricing methods without adding valuation logic to the
  product class.

## Time Conventions

Phase 2 starts with lightweight, extensible time-convention components:

```python
from datetime import date

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    WeekendCalendar,
    adjust,
)

year_fraction = Actual365Fixed().year_fraction(
    date(2026, 7, 2),
    date(2027, 7, 2),
)

payment_date = adjust(
    date(2026, 7, 4),
    WeekendCalendar(),
    BusinessDayConvention.FOLLOWING,
)
```

These components are intentionally independent from products and engines. Curves
and later rates products can reuse them without introducing global evaluation
dates or observer-style updates.

## Yield Curves

Phase 2 also introduces lightweight continuously compounded yield curves:

```python
from datetime import date

from option_pricer import Actual365Fixed, FlatYieldCurve, ZeroCurve

flat_curve = FlatYieldCurve(rate=0.05)
print(flat_curve.discount(1.0))

dated_curve = FlatYieldCurve(
    rate=0.05,
    reference_date=date(2026, 7, 2),
    day_count=Actual365Fixed(),
)
print(dated_curve.discount(date(2027, 7, 2)))

zero_curve = ZeroCurve(
    times=[1.0, 2.0, 3.0],
    zero_rates=[0.03, 0.04, 0.05],
)
print(zero_curve.zero_rate(1.5))
```

Curves support year-fraction inputs for research workflows and date inputs when
constructed with an explicit `reference_date` and `day_count`.

## Volatility Term Structures

Black volatility can also be represented as a flat volatility or an interpolated
term curve:

```python
from option_pricer import BlackVolCurve, FlatBlackVolatility

flat_vol = FlatBlackVolatility(0.20)
print(flat_vol.black_vol(1.0))

vol_curve = BlackVolCurve(
    times=[1.0, 2.0, 3.0],
    volatilities=[0.20, 0.22, 0.25],
)
print(vol_curve.black_vol(1.5))
```

`FlatVolatility` is kept as a compatibility alias for `FlatBlackVolatility`.
Strike is accepted by the `black_vol` API but ignored by Phase 2 flat and term
curves. This leaves room for smile and surface support later without forcing it
into the first volatility implementation.

## Phase 1 Scope

Supported:

- European vanilla call and put options.
- American vanilla call and put options through the binomial tree engine.
- Analytic Black-Scholes-Merton pricing for European vanilla options.
- Cox-Ross-Rubinstein binomial pricing.
- European terminal-spot Monte Carlo pricing.

Deferred to later phases:

- Calendar dates, holidays, business-day adjustment, and day-count conventions.
- Term structures and curve bootstrapping.
- FX, commodity, and interest-rate products.
- Observer, handle, lazy-evaluation, or global evaluation-date machinery.
