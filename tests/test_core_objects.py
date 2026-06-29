import math

import pytest

from option_pricer import (
    AmericanExercise,
    BlackScholesMertonProcess,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
    PricingResult,
    VanillaOption,
)


def test_plain_vanilla_call_payoff() -> None:
    payoff = PlainVanillaPayoff(OptionType.CALL, strike=100.0)

    assert payoff(90.0) == 0.0
    assert payoff(100.0) == 0.0
    assert payoff(110.0) == 10.0


def test_plain_vanilla_put_payoff() -> None:
    payoff = PlainVanillaPayoff(OptionType.PUT, strike=100.0)

    assert payoff(90.0) == 10.0
    assert payoff(100.0) == 0.0
    assert payoff(110.0) == 0.0


def test_payoff_validation() -> None:
    with pytest.raises(ValueError):
        PlainVanillaPayoff(OptionType.CALL, strike=0.0)

    with pytest.raises(TypeError):
        PlainVanillaPayoff("call", strike=100.0)  # type: ignore[arg-type]


def test_exercise_validation() -> None:
    assert EuropeanExercise(maturity=1.0).maturity == 1.0
    assert AmericanExercise(maturity=1.0).maturity == 1.0

    with pytest.raises(ValueError):
        EuropeanExercise(maturity=0.0)
    with pytest.raises(ValueError):
        AmericanExercise(maturity=0.0)


def test_vanilla_option_validation() -> None:
    option = VanillaOption(
        payoff=PlainVanillaPayoff(OptionType.CALL, 100.0),
        exercise=EuropeanExercise(1.0),
    )

    assert option.exercise.maturity == 1.0


def test_black_scholes_merton_process_helpers() -> None:
    process = BlackScholesMertonProcess(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.02,
        volatility=0.20,
    )

    assert process.discount_factor(1.0) == pytest.approx(math.exp(-0.05))
    assert process.dividend_discount_factor(1.0) == pytest.approx(math.exp(-0.02))
    assert process.forward(1.0) == pytest.approx(100.0 * math.exp(0.03))


def test_black_scholes_merton_process_validation() -> None:
    with pytest.raises(ValueError):
        BlackScholesMertonProcess(0.0, 0.05, 0.0, 0.20)
    with pytest.raises(ValueError):
        BlackScholesMertonProcess(100.0, 0.05, 0.0, 0.0)


def test_pricing_result_requires_finite_value() -> None:
    with pytest.raises(ValueError):
        PricingResult(float("nan"))
