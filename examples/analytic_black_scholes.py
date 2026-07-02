from option_pricer import (
    AnalyticBlackScholesEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
    VanillaOption,
)


def main() -> None:
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

    result = AnalyticBlackScholesEngine(process).calculate(option)

    print(f"value: {result.value:.6f}")
    if result.greeks is not None:
        print(f"delta: {result.greeks.delta:.6f}")
        print(f"gamma: {result.greeks.gamma:.6f}")
        print(f"vega:  {result.greeks.vega:.6f}")
        print(f"theta: {result.greeks.theta:.6f}")
        print(f"rho:   {result.greeks.rho:.6f}")


if __name__ == "__main__":
    main()
