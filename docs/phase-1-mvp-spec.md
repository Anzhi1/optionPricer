# Phase 1 MVP Specification

This document turns the Phase 0 architecture into an implementation plan for the
first working version of OptionPricer.

Phase 1 should prove the core design with the smallest useful pricing stack:

- one option instrument,
- one payoff family,
- European and American exercise definitions,
- one stochastic process,
- three pricing engines,
- structured results,
- focused tests.

## Goals

Phase 1 should answer these design questions through code:

- Can an instrument be priced by multiple engines without changing the
  instrument?
- Can payoff, exercise, process, and engine objects remain small and readable?
- Can the public API feel close to the financial concepts?
- Can numerical components be reused without building a heavy framework?

## Non-Goals

Phase 1 will not include:

- Calendar dates.
- Day-count conventions.
- Holiday calendars.
- Business-day adjustment.
- Yield curve bootstrapping.
- Volatility surfaces.
- FX, commodity, or interest-rate products.
- Observer, handle, or lazy-evaluation machinery.
- Calibration.
- Production market data containers.

## Numerical Conventions

To keep the first implementation transparent, Phase 1 uses simplified numerical
conventions:

- Time is represented as a year fraction `float`.
- Rates are continuously compounded annualized rates.
- Volatility is annualized Black volatility.
- Dividend yield is a continuously compounded annualized yield.
- Option values are expressed in the same currency or unit as the underlying.
- Greeks are calculated with respect to the current spot unless otherwise
  stated.
- `theta` is the derivative with respect to calendar time passing, so the
  analytic Black-Scholes theta is usually negative for long vanilla options.

These conventions should be written in docstrings for public classes and tested
where practical.

Date, calendar, holiday, and basis conventions start in Phase 2. Phase 1 classes
should not accept calendar dates yet; they should accept year fractions only.

## Public API Target

The first public usage should look like this:

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

assert result.value > 0.0
```

Phase 1 should expose the main user-facing classes from `option_pricer.__init__`
for convenience. Submodule imports should also work.

## Package Scope

Implement only the package files required by the MVP:

```text
option_pricer/
  __init__.py

  instruments/
    __init__.py
    base.py
    vanilla_option.py

  payoffs/
    __init__.py
    base.py
    vanilla.py

  exercise/
    __init__.py
    base.py
    european.py
    american.py

  processes/
    __init__.py
    black_scholes_merton.py

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

tests/
```

Defer `market`, `termstructures`, and richer numerical utilities until Phase 2
unless they are needed to keep the Phase 1 code clean.

## Domain Classes

### OptionType

Location: `option_pricer.payoffs.vanilla`

`OptionType` should be an enum:

```python
class OptionType(Enum):
    CALL = "call"
    PUT = "put"
```

String literals should not be accepted as a substitute in the first version.
Keeping the enum explicit prevents accidental misspellings in examples and
tests.

### Payoff

Location: `option_pricer.payoffs.base`

Initial protocol:

```python
class Payoff(Protocol):
    def __call__(self, underlying: float) -> float:
        ...
```

The payoff protocol should stay minimal. Engines only need to evaluate payoff
values.

### PlainVanillaPayoff

Location: `option_pricer.payoffs.vanilla`

Fields:

- `option_type: OptionType`
- `strike: float`

Validation:

- `strike > 0`
- `option_type` must be an `OptionType`

Behavior:

- Call payoff: `max(underlying - strike, 0.0)`
- Put payoff: `max(strike - underlying, 0.0)`

### Exercise

Location: `option_pricer.exercise.base`

Initial protocol:

```python
class Exercise(Protocol):
    @property
    def maturity(self) -> float:
        ...
```

Phase 1 only needs maturity for analytic and Monte Carlo engines. Tree engines
can inspect the concrete exercise type to decide whether early exercise is
allowed.

### EuropeanExercise

Location: `option_pricer.exercise.european`

Fields:

- `maturity: float`

Validation:

- `maturity > 0`

### AmericanExercise

Location: `option_pricer.exercise.american`

Fields:

- `maturity: float`

Validation:

- `maturity > 0`

Phase 1 supports the standard continuously exercisable American option from
valuation time to maturity. Deferred American exercise is deliberately excluded.

### Instrument

Location: `option_pricer.instruments.base`

Initial marker protocol:

```python
class Instrument(Protocol):
    pass
```

Avoid adding valuation methods to instruments in Phase 1.

### VanillaOption

Location: `option_pricer.instruments.vanilla_option`

Fields:

- `payoff: Payoff`
- `exercise: Exercise`

Validation:

- `payoff` must be callable.
- `exercise` must expose a positive `maturity`.

Phase 1 should keep this class deliberately small.

### BlackScholesMertonProcess

Location: `option_pricer.processes.black_scholes_merton`

Fields:

- `spot: float`
- `risk_free_rate: float`
- `dividend_yield: float`
- `volatility: float`

Validation:

- `spot > 0`
- `volatility > 0`

Rates and dividend yields may be negative. This keeps the process usable in
negative-rate environments and for assets with unusual carry assumptions.

Convenience methods:

- `discount_factor(maturity: float) -> float`
- `dividend_discount_factor(maturity: float) -> float`
- `forward(maturity: float) -> float`

## Result Classes

### Greeks

Location: `option_pricer.results.greeks`

Fields:

- `delta: float | None = None`
- `gamma: float | None = None`
- `vega: float | None = None`
- `theta: float | None = None`
- `rho: float | None = None`

Phase 1 analytic engine should populate all five fields. Tree and Monte Carlo
engines may leave Greeks as `None`.

### PricingResult

Location: `option_pricer.results.pricing_result`

Fields:

- `value: float`
- `greeks: Greeks | None = None`
- `diagnostics: dict[str, object] | None = None`

Validation:

- `value` should be finite.

Diagnostics are optional and may include engine-specific data such as number of
steps, number of paths, standard error, or random seed.

## Engine Interface

Location: `option_pricer.engines.base`

Initial protocol:

```python
class PricingEngine(Protocol):
    def calculate(self, instrument: Instrument) -> PricingResult:
        ...
```

Engines should raise `TypeError` for unsupported instrument or exercise types.
They should raise `ValueError` for invalid numerical configuration.

## Pricing Engines

### AnalyticBlackScholesEngine

Location: `option_pricer.engines.analytic.black_scholes`

Constructor:

```python
AnalyticBlackScholesEngine(process: BlackScholesMertonProcess)
```

Supported instruments:

- `VanillaOption`
- `PlainVanillaPayoff`
- `EuropeanExercise`

Unsupported:

- American exercise.

Outputs:

- option value,
- delta,
- gamma,
- vega,
- theta,
- rho.

Implementation notes:

- Use `math.erf` for normal CDF.
- Use standard Black-Scholes-Merton formulas with continuous dividend yield.
- Handle call and put through the same formula helpers.

### BinomialTreeEngine

Location: `option_pricer.engines.trees.binomial`

Constructor:

```python
BinomialTreeEngine(
    process: BlackScholesMertonProcess,
    steps: int = 200,
)
```

Supported instruments:

- `VanillaOption`
- `PlainVanillaPayoff`
- `EuropeanExercise`
- `AmericanExercise`

Validation:

- `steps > 0`

Implementation:

- Cox-Ross-Rubinstein tree.
- Risk-neutral probability using continuous dividend yield.
- Backward induction.
- For American exercise, compare continuation value with immediate exercise at
  each node.

Outputs:

- option value,
- diagnostics containing `steps`.

Greeks:

- leave `greeks=None` in the first implementation.

### EuropeanMonteCarloEngine

Location: `option_pricer.engines.monte_carlo.european_option`

Constructor:

```python
EuropeanMonteCarloEngine(
    process: BlackScholesMertonProcess,
    paths: int = 100_000,
    seed: int | None = None,
    antithetic: bool = False,
)
```

Supported instruments:

- `VanillaOption`
- `PlainVanillaPayoff`
- `EuropeanExercise`

Unsupported:

- American exercise.

Validation:

- `paths > 0`

Implementation:

- Simulate terminal spot directly under geometric Brownian motion.
- Use `numpy.random.default_rng(seed)`.
- Discount the average payoff by the risk-free discount factor.
- If `antithetic=True`, generate paired standard normals. This can be included in
  Phase 1 because it is small, educational, and useful for variance reduction.

Outputs:

- option value,
- diagnostics containing `paths`, `seed`, `antithetic`, and `standard_error`.

Greeks:

- leave `greeks=None` in the first implementation.

## Math Utilities

### Normal Distribution

Location: `option_pricer.math.distributions`

Functions:

- `normal_pdf(x: float) -> float`
- `normal_cdf(x: float) -> float`

Implementation:

- Use only the standard library.
- `normal_cdf` should use `math.erf`.

## Error Handling

Use built-in exceptions in Phase 1:

- `ValueError` for invalid values such as non-positive strike, maturity, spot,
  volatility, steps, or paths.
- `TypeError` for unsupported instrument, payoff, or exercise types.

Do not introduce custom exception classes until repeated patterns justify them.

## Testing Strategy

Use `pytest`.

### Unit Tests

Payoff tests:

- call payoff below, at, and above strike.
- put payoff below, at, and above strike.
- invalid strike.

Exercise tests:

- valid European maturity.
- invalid European maturity.
- valid American maturity.
- invalid American maturity.

Process tests:

- discount factor.
- dividend discount factor.
- forward formula.
- invalid spot and volatility.

### Analytic Engine Tests

Use a standard benchmark:

- spot: `100.0`
- strike: `100.0`
- risk-free rate: `0.05`
- dividend yield: `0.00`
- volatility: `0.20`
- maturity: `1.0`

Expected approximate values:

- call value: `10.4506`
- put value: `5.5735`
- call delta: `0.6368`
- put delta: `-0.3632`
- gamma: `0.0188`
- vega: `37.5240`
- call theta: approximately `-6.4140`
- put theta: approximately `-1.6579`
- call rho: `53.2325`
- put rho: `-41.8905`

Use tolerances appropriate to the number of decimals asserted.

### Binomial Engine Tests

- European call converges toward analytic Black-Scholes value as steps increase.
- European put converges toward analytic Black-Scholes value as steps increase.
- American put value is greater than or equal to European put value.
- American call with zero dividend yield should be close to European call value.

### Monte Carlo Engine Tests

- Fixed seed produces reproducible value.
- European call estimate is within a reasonable tolerance of analytic value.
- Standard error is positive.
- Antithetic mode produces a valid result and records diagnostics.

Use a loose enough tolerance to avoid flaky tests. The goal is to validate the
engine behavior, not to make Monte Carlo tests brittle.

## Implementation Order

Recommended sequence:

1. Package metadata and test setup.
2. Payoff and exercise classes.
3. Vanilla option and process classes.
4. Result classes and normal distribution utilities.
5. Analytic Black-Scholes engine.
6. Unit tests for the analytic path.
7. Binomial tree engine and tests.
8. Monte Carlo engine and tests.
9. Public exports in `option_pricer.__init__`.
10. Minimal README example.

This order creates a working pricing path early and then uses it as the
benchmark for the numerical engines.

## Phase 1 Exit Criteria

Phase 1 is complete when:

- A user can price a European call with the public API shown above.
- Analytic Black-Scholes values and Greeks match known benchmark values.
- The same `VanillaOption` can be priced by analytic, binomial, and Monte Carlo
  engines where supported.
- American put pricing works through the binomial engine.
- Tests cover validation and the main numerical behavior.
- The implementation does not introduce observer, handle, lazy-evaluation, or
  global evaluation-date machinery.
