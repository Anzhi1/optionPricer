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
