from option_pricer import (
    AnalyticBlackScholesEngine,
    Black76Process,
    Commodity,
    CommodityVanillaOption,
    Currency,
    EuropeanExercise,
    FlatBlackVolatility,
    FlatYieldCurve,
    ForwardCurve,
    OptionType,
    PlainVanillaPayoff,
)


gold = Commodity("XAU", name="Gold", unit="troy ounce")
usd = Currency("USD")

option = CommodityVanillaOption(
    commodity=gold,
    currency=usd,
    payoff=PlainVanillaPayoff(OptionType.CALL, strike=2400.0),
    exercise=EuropeanExercise(maturity=1.0),
    quantity=100.0,
)

process = Black76Process.from_forward_curve(
    forward_curve=ForwardCurve(times=[0.5, 1.0, 2.0], forwards=[2420.0, 2450.0, 2510.0]),
    maturity=option.exercise.maturity,
    discount_curve=FlatYieldCurve(rate=0.04),
    volatility=FlatBlackVolatility(0.18),
    strike=option.payoff.strike,
)

result = AnalyticBlackScholesEngine(process).calculate(option)

print(f"commodity: {gold.symbol}")
print(f"unit value: {result.value:.6f} {usd.code}/{gold.unit}")
print(f"notional value: {option.notional_value(result.value):.2f} {usd.code}")
