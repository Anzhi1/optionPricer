from option_pricer import (
    AnalyticBlackScholesEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    EuropeanMonteCarloEngine,
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

    analytic = AnalyticBlackScholesEngine(process).calculate(option)
    monte_carlo = EuropeanMonteCarloEngine(
        process,
        paths=100_000,
        seed=7,
        antithetic=True,
    ).calculate(option)

    assert monte_carlo.diagnostics is not None

    print(f"analytic value:    {analytic.value:.6f}")
    print(f"monte carlo value: {monte_carlo.value:.6f}")
    print(f"absolute error:    {abs(monte_carlo.value - analytic.value):.6f}")
    print(f"standard error:    {monte_carlo.diagnostics['standard_error']:.6f}")


if __name__ == "__main__":
    main()
