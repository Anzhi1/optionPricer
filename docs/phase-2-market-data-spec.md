# Phase 2 Market Data and Term Structure Specification

This document defines the second implementation phase for OptionPricer.

Phase 1 proved the core pricing architecture with flat numeric assumptions.
Phase 2 introduces the smallest useful set of market-convention and term
structure components needed to move beyond raw year fractions and flat numbers.

The goal is not to build a full QuantLib-style calendar and curve framework.
The goal is to add enough structure that later FX, commodity, and rates products
can reuse dates, day-count conventions, calendars, quotes, yield curves, and
volatility term structures without making simple option pricing cumbersome.

## Goals

Phase 2 should answer these design questions through code:

- Can curves use calendar dates without forcing all Phase 1 APIs to become date
  based?
- Can day-count, calendar, and business-day conventions stay small and explicit?
- Can flat Phase 1 inputs evolve into reusable term structures?
- Can market data be updated explicitly without observer, handle, or lazy-object
  machinery?
- Can old Phase 1 examples continue to work?

## Non-Goals

Phase 2 will not include:

- Full global holiday databases.
- Exchange-specific production calendar coverage.
- Full schedule-generation framework.
- Cashflow, coupon, bond, swap, or fixing-date logic.
- Curve bootstrapping from market instruments.
- Multi-curve construction.
- Volatility smiles, surfaces, cubes, or calibration.
- Observer, handle, lazy-evaluation, or global evaluation-date machinery.

## Design Principles

### Keep `datetime.date`

Use Python standard-library `datetime.date` instead of creating a custom Date
type.

Reasons:

- It is familiar to Python users.
- It avoids a large custom date API.
- It keeps interoperability with pandas, NumPy, CSV files, and notebooks easier.

The library may provide helper functions, but user-facing date inputs should be
plain `date` objects.

### Preserve Year-Fraction APIs

Phase 1 objects such as `EuropeanExercise(maturity=1.0)` should remain valid.

Date-based constructors should be additive:

```python
EuropeanExercise.from_dates(
    evaluation_date=date(2026, 7, 2),
    expiry_date=date(2027, 7, 2),
    day_count=Actual365Fixed(),
)
```

This keeps research experiments light while allowing real market dates when
needed.

### Explicit Market Data Updates

Market data should not silently notify dependent objects.

If a quote changes, the user should update the quote and explicitly recalculate:

```python
spot.value = 101.0
result = engine.calculate(option)
```

No observer graph, relinkable handle, or lazy recalculation should be introduced
in Phase 2.

### Curves Own Reference Dates

Date-based term structures should have an explicit `reference_date`.

For example:

```python
curve = FlatYieldCurve(
    reference_date=date(2026, 7, 2),
    rate=0.05,
    day_count=Actual365Fixed(),
)
```

When a method receives a date, the curve converts it to a year fraction using its
own reference date and day-count convention.

### Minimal But Extensible Conventions

Phase 2 should implement the smallest useful convention set, but the interfaces
must be designed so later market-specific conventions can be added without
rewriting curves, products, or engines.

This means:

- Day counters, calendars, and business-day conventions are public extension
  points, not private helper functions.
- Curves and products should depend on protocols or small shared interfaces, not
  concrete implementations such as `WeekendCalendar`.
- Adding a new day counter should not require changing curve classes.
- Adding a new calendar should not require changing business-day adjustment.
- Adding a new business-day convention may require extending the enum and adjust
  function, but should not require changing curve or product code.
- Market-specific calendars should be data/configuration-driven where possible,
  especially through explicit holiday sets in early versions.

The design should stay simple, but it should avoid hard-coding assumptions that
only work for the initial examples.

## Proposed Package Layout

Add the following packages and files:

```text
option_pricer/
  time/
    __init__.py
    daycounters.py
    calendars.py
    business_day.py

  market/
    __init__.py
    quotes.py

  termstructures/
    __init__.py
    yield_curve.py
    volatility.py

  math/
    interpolation.py
```

The package name `time` is intentionally domain-oriented. It contains financial
time conventions, not Python runtime timing utilities.

## Time Conventions

### DayCounter

Location: `option_pricer.time.daycounters`

Initial protocol:

```python
class DayCounter(Protocol):
    @property
    def name(self) -> str:
        ...

    def year_fraction(self, start: date, end: date) -> float:
        ...
```

Initial implementations:

- `Actual365Fixed`
- `Actual360`
- `Thirty360`

Validation:

- `end >= start`

Negative year fractions should not be supported in Phase 2.

Extensibility rules:

- A day counter is any object implementing `year_fraction(start, end)`.
- Day counters should be stateless when possible.
- If a future convention needs parameters, represent them as dataclass fields
  rather than special cases in curve code.
- Do not create a central registry in Phase 2. Users can pass day-counter
  objects directly.

Example future extension:

```python
@dataclass(frozen=True)
class ActualActualIsda:
    name: str = "Actual/Actual ISDA"

    def year_fraction(self, start: date, end: date) -> float:
        ...
```

### Actual365Fixed

Formula:

```text
(end - start).days / 365.0
```

### Actual360

Formula:

```text
(end - start).days / 360.0
```

### Thirty360

Phase 2 should implement a simple 30/360 US-style convention only if it is needed
by tests or examples. If it feels like a distraction, defer it and start with
`Actual365Fixed` and `Actual360`.

### Calendar

Location: `option_pricer.time.calendars`

Initial protocol:

```python
class Calendar(Protocol):
    @property
    def name(self) -> str:
        ...

    def is_business_day(self, day: date) -> bool:
        ...
```

Initial implementations:

- `NullCalendar`
- `WeekendCalendar`
- `HolidayCalendar`

Behavior:

- `NullCalendar`: every date is a business day.
- `WeekendCalendar`: Saturday and Sunday are not business days.
- `HolidayCalendar`: weekends plus an explicit set of holiday dates are not
  business days.

No country- or exchange-specific holiday rules should be hard-coded in Phase 2.

Extensibility rules:

- A calendar is any object implementing `is_business_day(day)`.
- Calendar implementations should be composable through explicit data rather than
  hidden global tables.
- `HolidayCalendar` should accept a name, weekend weekday set, and explicit
  holiday dates.
- Future exchange calendars can wrap or subclass `HolidayCalendar`, but Phase 2
  should not require inheritance.
- Calendar logic should not know about day-count conventions or curves.

Suggested `HolidayCalendar` shape:

```python
@dataclass(frozen=True)
class HolidayCalendar:
    name: str
    holidays: frozenset[date]
    weekend_days: frozenset[int] = frozenset({5, 6})

    def is_business_day(self, day: date) -> bool:
        return day.weekday() not in self.weekend_days and day not in self.holidays
```

This lets users create research calendars without waiting for a built-in market
calendar database:

```python
china_example = HolidayCalendar(
    name="China example",
    holidays=frozenset({date(2026, 10, 1), date(2026, 10, 2)}),
)
```

### BusinessDayConvention

Location: `option_pricer.time.business_day`

Initial enum:

```python
class BusinessDayConvention(Enum):
    FOLLOWING = "following"
    MODIFIED_FOLLOWING = "modified_following"
    PRECEDING = "preceding"
    UNADJUSTED = "unadjusted"
```

Function:

```python
adjust(day: date, calendar: Calendar, convention: BusinessDayConvention) -> date
```

Rules:

- `UNADJUSTED`: return the input date.
- `FOLLOWING`: move forward to the next business day.
- `PRECEDING`: move backward to the previous business day.
- `MODIFIED_FOLLOWING`: move forward unless that crosses into a new month; if it
  does, move backward instead.

Extensibility rules:

- Keep adjustment as a function so products, schedules, and curves can share the
  same behavior.
- The function should depend only on `date`, `Calendar`, and
  `BusinessDayConvention`.
- Do not embed calendar-specific rules in the convention enum.
- Future conventions such as `MODIFIED_PRECEDING`, `NEAREST`, or IMM-specific
  rules should be added deliberately when a product requires them.
- If a future convention needs parameters, introduce a separate convention object
  rather than overloading the enum with hidden behavior.

For Phase 2, an enum is enough. If later conventions become parameterized, the
API can evolve toward:

```python
class DateAdjustment(Protocol):
    def adjust(self, day: date, calendar: Calendar) -> date:
        ...
```

but this abstraction should not be introduced until the enum starts to constrain
real use cases.

## Market Data

### SimpleQuote

Location: `option_pricer.market.quotes`

Fields:

- `value: float`

Behavior:

- Mutable by explicit assignment.
- Must always be finite.

Example:

```python
spot = SimpleQuote(100.0)
spot.value = 101.0
```

This gives users a lightweight quote object without introducing observer
machinery.

## Yield Term Structures

### YieldTermStructure

Location: `option_pricer.termstructures.yield_curve`

Initial protocol:

```python
class YieldTermStructure(Protocol):
    def discount(self, maturity: float | date) -> float:
        ...

    def zero_rate(self, maturity: float | date) -> float:
        ...
```

Phase 2 should support both year-fraction and date inputs where the curve has a
reference date.

### FlatYieldCurve

Fields:

- `rate: float`
- `reference_date: date | None = None`
- `day_count: DayCounter | None = None`

Behavior:

- Rate is continuously compounded.
- `discount(t) = exp(-rate * t)`
- `zero_rate(t) = rate`

Validation:

- If `reference_date` is provided, `day_count` must also be provided.
- Date inputs require both `reference_date` and `day_count`.
- Maturities must be non-negative.

### ZeroCurve

Fields:

- `times: Sequence[float]`
- `zero_rates: Sequence[float]`
- optional `reference_date`
- optional `day_count`

Behavior:

- Store continuously compounded zero rates.
- Use linear interpolation on zero rates.
- Extrapolation should be explicit. Phase 2 can either disallow extrapolation or
  flat-extrapolate endpoint rates. Prefer disallowing extrapolation first.

Validation:

- Times must be strictly increasing.
- First time should be positive.
- Number of times and rates must match.

### DiscountCurve

Fields:

- `times: Sequence[float]`
- `discount_factors: Sequence[float]`
- optional `reference_date`
- optional `day_count`

Behavior:

- Interpolate log discount factors linearly.
- Convert interpolated discount factors to zero rates when requested.

Validation:

- Times must be strictly increasing.
- Discount factors must be positive.
- Number of times and discount factors must match.

## Volatility Term Structures

### BlackVolTermStructure

Location: `option_pricer.termstructures.volatility`

Initial protocol:

```python
class BlackVolTermStructure(Protocol):
    def black_vol(self, maturity: float | date, strike: float | None = None) -> float:
        ...
```

Strike is optional in Phase 2 because the first implementation is flat or term
only. It leaves room for later smile and surface designs without forcing them
now.

### FlatBlackVolatility

Fields:

- `volatility: float`
- optional `reference_date`
- optional `day_count`

Validation:

- `volatility > 0`

`FlatVolatility` may be kept as a compatibility alias, but new examples and
documentation should prefer `FlatBlackVolatility` to make the Black implied-vol
semantics explicit.

### BlackVolCurve

Fields:

- `times: Sequence[float]`
- `volatilities: Sequence[float]`
- optional `reference_date`
- optional `day_count`

Behavior:

- Linear interpolation on volatility.
- No smile or strike dependence in Phase 2.

## Updating BlackScholesMertonProcess

Phase 1 process:

```python
BlackScholesMertonProcess(
    spot=100.0,
    risk_free_rate=0.05,
    dividend_yield=0.0,
    volatility=0.20,
)
```

Phase 2 should keep this valid.

Add a term-structure constructor rather than replacing the dataclass fields
immediately:

```python
process = BlackScholesMertonProcess.from_term_structures(
    spot=SimpleQuote(100.0),
    maturity=1.0,
    risk_free_curve=FlatYieldCurve(rate=0.05),
    dividend_curve=FlatYieldCurve(rate=0.0),
    volatility=FlatBlackVolatility(0.20),
)
```

This avoids breaking Phase 1 code while opening a path toward reusable market
data.

The constructor should use snapshot semantics: it reads the current quote, curve,
and volatility values for the supplied maturity and returns an ordinary flat
`BlackScholesMertonProcess`. Updating the quote later should not mutate existing
process objects.

The internal representation can stay flat in Phase 2 if that keeps the code
simple, but the API should make the intended direction clear.

## Interpolation Utilities

Location: `option_pricer.math.interpolation`

Initial functions:

- `linear_interpolate(x, xs, ys) -> float`

Validation:

- `xs` must be strictly increasing.
- no extrapolation by default.

Do not introduce an interpolation class hierarchy until multiple interpolation
methods are needed.

## Testing Strategy

Use `pytest`.

Day-count tests:

- Actual/365 over one calendar year.
- Actual/360 over known day ranges.
- invalid reversed dates.

Calendar tests:

- Null calendar accepts weekends.
- Weekend calendar rejects Saturday and Sunday.
- Holiday calendar rejects explicit holidays.

Business-day tests:

- Following adjustment.
- Modified following month-crossing behavior.
- Preceding adjustment.
- Unadjusted returns original date.

Curve tests:

- Flat discount factor and zero rate.
- Date-based and time-based flat curve inputs match.
- Zero curve interpolation.
- Discount curve log-discount interpolation.
- invalid curve inputs.

Volatility tests:

- Flat volatility.
- Volatility curve interpolation.
- invalid volatility.

Process integration tests:

- `BlackScholesMertonProcess.from_term_structures` matches Phase 1 flat numeric
  pricing for a European option.
- Phase 1 constructor examples still work unchanged.

## Implementation Order

Recommended sequence:

1. `time.daycounters`
2. `time.calendars`
3. `time.business_day`
4. `market.quotes`
5. `math.interpolation`
6. `termstructures.yield_curve`
7. `termstructures.volatility`
8. `BlackScholesMertonProcess.from_term_structures`
9. Tests for each layer.
10. Examples showing date-based curves.

This order starts with small pure components and only then connects them to
pricing.

## Phase 2 Exit Criteria

Phase 2 is complete when:

- Flat and interpolated yield curves can return discount factors and zero rates.
- Flat and interpolated volatility term structures can return Black volatility.
- Date-based curves can convert dates to year fractions through explicit
  day-count conventions.
- Minimal calendars and business-day adjustment work.
- Quotes can be updated explicitly without observer or handle machinery.
- Phase 1 option pricing examples still run unchanged.
- A new example prices a European option using term-structure-based market data.
