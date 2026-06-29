import pytest

from option_pricer import (
    AnalyticBlackScholesEngine,
    AmericanExercise,
    BinomialTreeEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
    VanillaOption,
)


def make_process(dividend_yield: float = 0.0) -> BlackScholesMertonProcess:
    return BlackScholesMertonProcess(100.0, 0.05, dividend_yield, 0.20)


def make_option(option_type: OptionType, exercise: object) -> VanillaOption:
    return VanillaOption(PlainVanillaPayoff(option_type, 100.0), exercise)  # type: ignore[arg-type]


def test_binomial_european_call_converges_to_analytic_value() -> None:
    process = make_process()
    option = make_option(OptionType.CALL, EuropeanExercise(1.0))

    analytic = AnalyticBlackScholesEngine(process).calculate(option).value
    tree = BinomialTreeEngine(process, steps=500).calculate(option)

    assert tree.value == pytest.approx(analytic, abs=0.02)
    assert tree.diagnostics == {"steps": 500}


def test_binomial_european_put_converges_to_analytic_value() -> None:
    process = make_process()
    option = make_option(OptionType.PUT, EuropeanExercise(1.0))

    analytic = AnalyticBlackScholesEngine(process).calculate(option).value
    tree = BinomialTreeEngine(process, steps=500).calculate(option)

    assert tree.value == pytest.approx(analytic, abs=0.02)


def test_american_put_is_at_least_european_put() -> None:
    process = make_process()
    european = make_option(OptionType.PUT, EuropeanExercise(1.0))
    american = make_option(OptionType.PUT, AmericanExercise(1.0))

    european_value = BinomialTreeEngine(process, steps=300).calculate(european).value
    american_value = BinomialTreeEngine(process, steps=300).calculate(american).value

    assert american_value >= european_value


def test_american_call_without_dividend_is_close_to_european_call() -> None:
    process = make_process(dividend_yield=0.0)
    european = make_option(OptionType.CALL, EuropeanExercise(1.0))
    american = make_option(OptionType.CALL, AmericanExercise(1.0))

    european_value = BinomialTreeEngine(process, steps=300).calculate(european).value
    american_value = BinomialTreeEngine(process, steps=300).calculate(american).value

    assert american_value == pytest.approx(european_value, abs=1e-10)
