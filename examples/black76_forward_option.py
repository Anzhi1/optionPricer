from option_pricer import (
    AnalyticBlackScholesEngine,
    Black76Process,
    EuropeanExercise,
    FlatBlackVolatility,
    FlatYieldCurve,
    OptionType,
    PlainVanillaPayoff,
    SimpleQuote,
    VanillaOption,
)


option = VanillaOption(
    payoff=PlainVanillaPayoff(OptionType.CALL, strike=100.0),
    exercise=EuropeanExercise(maturity=1.0),
)

process = Black76Process.from_term_structures(
    forward=SimpleQuote(100.0),
    maturity=option.exercise.maturity,
    discount_curve=FlatYieldCurve(rate=0.05),
    volatility=FlatBlackVolatility(0.20),
    strike=100.0,
)

result = AnalyticBlackScholesEngine(process).calculate(option)

print(f"value: {result.value:.6f}")
print(f"forward delta: {result.greeks.delta:.6f}")
