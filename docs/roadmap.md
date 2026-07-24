# OptionPricer Roadmap

OptionPricer is a QuantLib-inspired pricing and valuation library for learning,
research, and transparent financial engineering experiments.

The project should inherit the useful conceptual separation from QuantLib while
avoiding framework machinery that is unnecessary for the first research-oriented
versions. In particular, the initial design avoids observer graphs, handles,
lazy evaluation, deep inheritance trees, and implicit global state.

## Design Philosophy

The library should make financial logic easy to see.

- Keep product definitions separate from pricing algorithms.
- Keep market data, stochastic processes, and pricing engines separate.
- Distinguish asset classes through concrete components, not top-level package
  partitions.
- Prefer explicit construction and function calls over implicit updates.
- Prefer shallow abstractions and composition over deep inheritance.
- Use reusable numerical and financial components where they reduce real
  duplication.
- Keep the first version small enough that every concept can be understood by a
  new developer.

## Phase 0: Design Baseline

Goal: define the architecture before writing the first pricing engine.

Deliverables:

- Project roadmap.
- First-stage architecture document.
- Phase 1 MVP specification.
- Initial package layout proposal.
- Naming conventions and API style.
- Asset-class boundary principles.
- MVP scope and non-goals.

Exit criteria:

- The main domain concepts are named.
- The first supported product and engines are selected.
- The boundaries between instruments, payoffs, exercises, processes, market data,
  engines, results, and math utilities are clear.
- The framework has a clear rule for adding equity, FX, rates, and commodity
  components without splitting the project into isolated asset-class silos.

## Phase 1: Vanilla Equity Option MVP

Goal: build a clean end-to-end option pricing flow.

Implementation details are defined in `docs/phase-1-mvp-spec.md`.

Scope:

- European and American vanilla options.
- Plain vanilla call and put payoff.
- Flat risk-free rate, dividend yield, and volatility.
- Black-Scholes-Merton process.
- Analytic Black-Scholes engine for European options.
- Cox-Ross-Rubinstein binomial engine for European and American options.
- Basic Monte Carlo engine for European options.
- Pricing result object with value and selected Greeks.
- Unit tests against known textbook values.

Non-goals:

- Full calendar system.
- Full day-count convention framework.
- Yield curve bootstrapping.
- Volatility surface calibration.
- Observer or handle-style market data updates.
- Production risk system concerns.

## Phase 2: Term Structures and Market Data

Goal: move from flat assumptions to reusable market data abstractions.

Implementation details are defined in `docs/phase-2-market-data-spec.md`.

Scope:

- Date utilities needed by term structures.
- Minimal day-count or basis conventions.
- Minimal calendar and holiday support.
- Simple business-day adjustment.
- Zero curve and discount curve interfaces.
- Basic interpolation.
- Simple volatility term structure.
- Quote containers with explicit updates.
- Tests for discount factors, forwards, and interpolated values.

Non-goals:

- Full global holiday database.
- Full exchange-specific calendar coverage.
- Full schedule-generation framework.
- Production market data storage.

## Phase 3: Foreign Exchange and Commodity Options

Goal: test whether the option architecture extends cleanly beyond equity-style
spot products before introducing the larger rates cashflow framework.

Status: implemented for the first research-oriented scope.

Scope:

- Currency and currency-pair descriptors.
- FX option instrument or conventions where needed.
- Garman-Kohlhagen process.
- Black-76 forward option process.
- Commodity or precious-metal option examples.
- Forward curve support where needed.
- Tests showing reuse of payoff, exercise, results, and selected engines.

Non-goals:

- Full cross-currency curve construction.
- Full commodity storage and delivery modeling.
- Precious-metal market conventions beyond simple research examples.

Implemented:

- `Currency` and `CurrencyPair`.
- `FxVanillaOption` with explicit base notional scaling.
- `GarmanKohlhagenProcess`.
- `Black76Process`.
- `FlatForwardCurve` and `ForwardCurve`.
- `Commodity` and `CommodityVanillaOption`.
- FX, Black-76 forward, and gold Black-76 examples.
- Reuse of payoff, exercise, results, and Black-style analytic, Monte Carlo,
  and tree engines where the lognormal model assumptions match.

Deferred:

- FX delta conventions.
- Premium-adjusted Greeks.
- FX volatility smile/surface construction.
- ATM/risk-reversal/butterfly quote conversion.
- Commodity storage, delivery, location, lease-rate, and futures margining
  conventions.
- General-purpose Monte Carlo or tree frameworks for arbitrary future models.

## Phase 4: Interest Rate Products

Goal: introduce fixed-income instruments and curve-based valuation after the
date, day-count, calendar, and curve foundations exist.

Implementation details are defined in `docs/phase-4-rates-spec.md`.

Status: first fixed-income slice implemented. Schedule generation, dated
cashflows, fixed-rate coupons, fixed-rate bonds, and bond discounting are in
place. Forward-rate projection, forward-rate curves, lightweight Ibor indexes,
floating-rate coupons, floating-rate notes, and vanilla interest-rate swaps are
also implemented.

Scope:

- Schedule generation.
- Cashflow abstraction.
- Discounting engine.
- Fixed-rate bonds.
- Floating-rate notes.
- Vanilla interest rate swaps.
- Basic forward-rate projection.

Implemented:

- `Schedule`, `Frequency`, `DateGenerationRule`, and `generate_schedule`.
- `FixedCashflow` and `FixedRateCoupon`.
- `fixed_rate_leg(...)` and `floating_rate_leg(...)` cashflow helpers.
- Optional payment-date adjustment in cashflow leg builders.
- `DiscountingCashflowEngine`.
- `FixedRateBond`.
- `DiscountingBondEngine`.
- Simple `forward_rate(...)` projection from discount factors.
- `FlatForwardRateCurve` and `ForwardRateCurve`.
- `IborIndex`.
- `FloatingRateCoupon`.
- `FloatingRateNote`.
- `VanillaInterestRateSwap` and `SwapType`.
- `DiscountingSwapEngine`.
- Tests and examples for the fixed-rate bond discounting path.
- Tests and examples for the floating-rate note discounting path.
- Tests and examples for vanilla fixed-vs-floating swap discounting.

Deferred:

- Fixing-date infrastructure.

Non-goals:

- Full multi-curve production framework.
- Complete market convention database.
- Complex callable or structured rates products.

## Phase 5: Advanced Models and Engines

Goal: add research-oriented models without compromising the core design.

Candidates:

- Heston model.
- Hull-White model.
- Local volatility.
- Finite-difference engines.
- Longstaff-Schwartz Monte Carlo.
- Calibration utilities.

## Phase 6: Usability and Research Tooling

Goal: make the library pleasant to use for experiments.

Scope:

- Examples and notebooks.
- Result comparison utilities.
- Plotting helpers.
- Scenario analysis.
- Simple benchmarking.
- Documentation for extending products and engines.
