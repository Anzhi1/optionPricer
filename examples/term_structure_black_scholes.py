from datetime import date

from option_pricer import (
    Actual365Fixed,
    AnalyticBlackScholesEngine,
    BlackScholesMertonProcess,
    BlackVolCurve,
    EuropeanExercise,
    FlatYieldCurve,
    OptionType,
    PlainVanillaPayoff,
    SimpleQuote,
    VanillaOption,
    ZeroCurve,
)


evaluation_date = date(2026, 7, 2)
expiry_date = date(2027, 7, 2)
day_count = Actual365Fixed()

option = VanillaOption(
    payoff=PlainVanillaPayoff(OptionType.CALL, strike=100.0),
    exercise=EuropeanExercise.from_dates(
        evaluation_date=evaluation_date,
        expiry_date=expiry_date,
        day_count=day_count,
    ),
)

spot = SimpleQuote(100.0)
risk_free_curve = ZeroCurve(
    times=[0.5, 1.0, 2.0],
    zero_rates=[0.045, 0.05, 0.055],
    reference_date=evaluation_date,
    day_count=day_count,
)
dividend_curve = FlatYieldCurve(
    rate=0.02,
    reference_date=evaluation_date,
    day_count=day_count,
)
volatility = BlackVolCurve(
    times=[0.5, 1.0, 2.0],
    volatilities=[0.18, 0.20, 0.22],
    reference_date=evaluation_date,
    day_count=day_count,
)

process = BlackScholesMertonProcess.from_term_structures(
    spot=spot,
    maturity=expiry_date,
    risk_free_curve=risk_free_curve,
    dividend_curve=dividend_curve,
    volatility=volatility,
    strike=100.0,
)

engine = AnalyticBlackScholesEngine(process)
result = engine.calculate(option)

print(f"value: {result.value:.6f}")
print(f"delta: {result.greeks.delta:.6f}")
