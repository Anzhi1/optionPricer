from option_pricer import (
    AnalyticBlackScholesEngine,
    Currency,
    CurrencyPair,
    EuropeanExercise,
    FlatBlackVolatility,
    FlatYieldCurve,
    GarmanKohlhagenProcess,
    OptionType,
    PlainVanillaPayoff,
    SimpleQuote,
    VanillaOption,
)


pair = CurrencyPair(Currency("EUR"), Currency("USD"))

option = VanillaOption(
    payoff=PlainVanillaPayoff(OptionType.CALL, strike=1.12),
    exercise=EuropeanExercise(maturity=1.0),
)

process = GarmanKohlhagenProcess.from_term_structures(
    spot=SimpleQuote(1.10),
    maturity=option.exercise.maturity,
    domestic_curve=FlatYieldCurve(rate=0.05),
    foreign_curve=FlatYieldCurve(rate=0.02),
    volatility=FlatBlackVolatility(0.12),
    pair=pair,
    strike=1.12,
)

result = AnalyticBlackScholesEngine(process).calculate(option)

print(f"pair: {pair.symbol}")
print(f"value: {result.value:.6f}")
print(f"delta: {result.greeks.delta:.6f}")
