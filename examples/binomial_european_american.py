from option_pricer import (
    AmericanExercise,
    AnalyticBlackScholesEngine,
    BinomialTreeEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
    VanillaOption,
)


def main() -> None:
    process = BlackScholesMertonProcess(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )
    payoff = PlainVanillaPayoff(OptionType.PUT, strike=100.0)

    european_put = VanillaOption(payoff=payoff, exercise=EuropeanExercise(maturity=1.0))
    american_put = VanillaOption(payoff=payoff, exercise=AmericanExercise(maturity=1.0))

    analytic_value = AnalyticBlackScholesEngine(process).calculate(european_put).value
    tree = BinomialTreeEngine(process, steps=500)

    european_tree_value = tree.calculate(european_put).value
    american_tree_value = tree.calculate(american_put).value

    print(f"analytic european put: {analytic_value:.6f}")
    print(f"tree european put:     {european_tree_value:.6f}")
    print(f"tree american put:     {american_tree_value:.6f}")
    print(f"early exercise value:  {american_tree_value - european_tree_value:.6f}")


if __name__ == "__main__":
    main()
