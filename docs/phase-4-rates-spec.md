# Phase 4 Rates Specification

This document defines the first interest-rate product phase for OptionPricer.

Phase 4 should introduce fixed-income valuation through schedules, cashflows,
and discounting. It should not start with swaps directly. Rates products depend
on dates, calendars, day-count conventions, and yield curves, so the first step
is to make those foundations reusable in a small cashflow framework.

Status: the first fixed-income slice described in this document has been
implemented. The second Phase 4 slice has started with simple forward-rate
projection, forward-rate curves, lightweight Ibor indexes, and floating-rate
coupons. Floating-rate notes and vanilla interest-rate swaps are also
implemented. The next work should harden rates conventions and add richer
testing around leg-level behavior.

## Goals

- Add a minimal schedule-generation utility.
- Add fixed cashflow abstractions.
- Add a discounting engine that prices dated cashflows from a yield term
  structure.
- Add a simple fixed-rate bond before floating-rate notes or swaps.
- Keep date and convention handling explicit.
- Reuse Phase 2 day counters, calendars, business-day adjustment, and yield
  term structures.

## Non-Goals

- Full market convention database.
- Full multi-curve framework.
- Bootstrapping curves from deposits, futures, bonds, or swaps.
- Floating-rate reset/fixing infrastructure in the first step.
- Stub-period convention completeness.
- Ex-coupon periods, amortization, callable bonds, inflation bonds, or credit
  risky cashflows.
- Production schedule generation covering every market edge case.

## Package Additions

```text
option_pricer/
  schedules/
    __init__.py
    schedule.py

  cashflows/
    __init__.py
    cashflow.py
    fixed_rate.py
    floating_rate.py
    legs.py

  indexes/
    __init__.py
    ibor.py

  termstructures/
    forward_rate_curve.py

  instruments/
    rates/
      __init__.py
      bonds.py

  engines/
    discounting/
      __init__.py
      cashflows.py
      bond.py
      swap.py
```

The package layout keeps rates instruments under `instruments/rates`, but shared
schedule and cashflow components live outside that subpackage so future swaps,
FRNs, and other fixed-income products can reuse them.

## Schedule

Location: `option_pricer.schedules.schedule`

Initial objects:

- `Frequency`
- `DateGenerationRule`
- `Schedule`
- `generate_schedule(...)`

Initial frequency values:

- `ANNUAL`
- `SEMIANNUAL`
- `QUARTERLY`
- `MONTHLY`

Initial generation rules:

- `FORWARD`
- `BACKWARD`

Inputs:

- `start_date: date`
- `end_date: date`
- `frequency: Frequency`
- `calendar: Calendar`
- `business_day_convention: BusinessDayConvention`
- `date_generation_rule: DateGenerationRule = DateGenerationRule.FORWARD`

Behavior:

- Return an ordered list of adjusted schedule dates.
- Include start and end dates.
- Apply the business-day convention to generated dates.
- Keep month-end handling minimal in the first implementation.

Validation:

- `end_date > start_date`
- known frequency
- known generation rule

Deferred:

- end-of-month rules
- first/next-to-last date stubs
- IMM rules
- holiday-calendar databases

## Cashflows

Location: `option_pricer.cashflows`

Initial protocol:

```python
class Cashflow(Protocol):
    payment_date: date

    def amount(self) -> float:
        ...
```

Initial implementation:

```python
@dataclass(frozen=True)
class FixedCashflow:
    payment_date: date
    value: float

    def amount(self) -> float:
        return value
```

Fixed-rate coupons should be explicit dated cashflows:

```python
@dataclass(frozen=True)
class FixedRateCoupon:
    accrual_start: date
    accrual_end: date
    payment_date: date
    notional: float
    fixed_rate: float
    day_count: DayCounter

    def amount(self) -> float:
        return notional * fixed_rate * day_count.year_fraction(accrual_start, accrual_end)
```

Principal redemption can be represented as `FixedCashflow` in the first
implementation.

Floating-rate coupons start with projected, not fixed, rates:

```python
@dataclass(frozen=True)
class FloatingRateCoupon:
    accrual_start: date
    accrual_end: date
    payment_date: date
    notional: float
    spread: float
    day_count: DayCounter
    index: IborIndex

    def rate(self) -> float:
        return index.rate(accrual_start, accrual_end) + spread

    def amount(self) -> float:
        return notional * rate() * day_count.year_fraction(accrual_start, accrual_end)
```

The first implementation uses a lightweight `IborIndex` to hold index
conventions and a projection curve. It deliberately avoids historical fixings,
fixing lag, settlement-day rules, and an index manager until floating-rate notes
need them.

Leg builders in `option_pricer.cashflows.legs` provide small reusable helpers
for building fixed and floating coupon sequences from schedules. They are plain
functions, not a builder framework, so products can share coupon generation
without hiding the financial logic.

Leg builders default each coupon payment date to the accrual end date. They also
accept an optional payment calendar and business-day convention so products can
adjust payment dates without changing accrual start or accrual end dates.

## Discounting Engine

Location: `option_pricer.engines.discounting.cashflows`

Initial shape:

```python
@dataclass(frozen=True)
class DiscountingCashflowEngine:
    discount_curve: YieldTermStructure

    def present_value(self, cashflows: Sequence[Cashflow]) -> float:
        ...
```

Behavior:

- Sum `cashflow.amount() * discount_curve.discount(cashflow.payment_date)`.
- Date-based discounting requires the curve to have `reference_date` and
  `day_count`.
- Ignore cashflows with payment dates before the curve reference date only after
  an explicit policy exists. In the first implementation, let the curve reject
  negative maturities.

## Fixed-Rate Bond

Location: `option_pricer.instruments.rates.bonds`

Initial fields:

- `notional: float`
- `fixed_rate: float`
- `schedule: Schedule`
- `day_count: DayCounter`

Behavior:

- Generate fixed coupons from adjacent schedule dates.
- Add principal redemption on the final schedule date.
- Return cashflows through `cashflows()`.

Validation:

- `notional > 0`
- schedule has at least two dates
- fixed rates may be negative

Initial pricing:

```python
bond = FixedRateBond(...)
engine = DiscountingBondEngine(discount_curve)
result = engine.calculate(bond)
```

`DiscountingBondEngine` can be a thin wrapper around `DiscountingCashflowEngine`
that returns `PricingResult(value=pv)`.

## Floating-Rate Note

Location: `option_pricer.instruments.rates.bonds`

Initial fields:

- `notional: float`
- `spread: float`
- `schedule: Schedule`
- `index: IborIndex`

Behavior:

- Generate floating coupons from adjacent schedule dates.
- Use the index day counter as the coupon accrual day counter.
- Add principal redemption on the final schedule date.
- Return cashflows through `cashflows()`.

Initial pricing reuses `DiscountingBondEngine`; the engine accepts instruments
that expose `cashflows()`.

## Vanilla Interest-Rate Swap

Location: `option_pricer.instruments.rates.swaps`

Initial fields:

- `swap_type: SwapType`
- `notional: float`
- `fixed_rate: float`
- `fixed_schedule: Schedule`
- `fixed_day_count: DayCounter`
- `floating_schedule: Schedule`
- `index: IborIndex`
- `spread: float = 0.0`

Behavior:

- `SwapType.PAYER` means pay fixed and receive floating.
- `SwapType.RECEIVER` means receive fixed and pay floating.
- Generate fixed coupons from the fixed schedule.
- Generate floating coupons from the floating schedule.
- Do not exchange notional.

Initial pricing uses `DiscountingSwapEngine`, which discounts each leg and
returns diagnostics for `fixed_leg_pv`, `floating_leg_pv`, and `fair_rate`.
The engine also exposes `fixed_leg_annuity(...)` and `fair_rate(...)` for
research workflows.

## Testing Strategy

Schedule tests:

- annual forward schedule.
- semiannual backward schedule.
- business-day adjustment.
- invalid date order.

Cashflow tests:

- fixed cashflow amount.
- fixed-rate coupon accrual amount.
- invalid notional.

Discounting tests:

- single cashflow present value.
- multiple cashflow present value.
- date-based curve discounting.

Bond tests:

- fixed-rate bond cashflow generation.
- zero-coupon-like bond through coupon rate zero.
- discounting engine prices generated cashflows consistently with manual PV.

## Implementation Order

1. `schedules.schedule`
2. schedule tests
3. `cashflows.cashflow` and `cashflows.fixed_rate`
4. cashflow tests
5. `engines.discounting.cashflows`
6. discounting tests
7. `instruments.rates.bonds`
8. `engines.discounting.bond`
9. bond tests and example

This order keeps the rates stack honest: dates first, cashflows second, product
composition third, pricing last.

## Phase 4 First Exit Criteria

- A schedule can be generated from start date, end date, frequency, calendar,
  and business-day convention.
- Fixed dated cashflows and fixed-rate coupons can produce amounts.
- Dated cashflows can be discounted from a date-based yield curve.
- A simple fixed-rate bond can generate coupons and principal.
- A discounting bond engine can price the fixed-rate bond.
- Tests cover schedule, cashflow, discounting, and bond behavior.

Current implementation satisfies these criteria through:

- `option_pricer.schedules.schedule`
- `option_pricer.cashflows.cashflow`
- `option_pricer.cashflows.fixed_rate`
- `option_pricer.cashflows.floating_rate`
- `option_pricer.cashflows.legs`
- `option_pricer.engines.discounting.cashflows`
- `option_pricer.instruments.rates.bonds`
- `option_pricer.instruments.rates.swaps`
- `option_pricer.engines.discounting.bond`
- `option_pricer.engines.discounting.swap`
- `tests/test_floating_rate_notes.py`
- `tests/test_interest_rate_swaps.py`
- `tests/test_schedules.py`
- `tests/test_cashflows.py`
- `tests/test_discounting_cashflows.py`
- `tests/test_fixed_rate_bonds.py`
- `examples/fixed_rate_bond.py`
