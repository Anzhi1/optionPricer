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
