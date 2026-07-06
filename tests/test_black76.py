import math

import pytest

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


def make_option(option_type: OptionType) -> VanillaOption:
    return VanillaOption(
        payoff=PlainVanillaPayoff(option_type, strike=100.0),
        exercise=EuropeanExercise(maturity=1.0),
    )


def test_black76_process_helpers() -> None:
    process = Black76Process(forward=100.0, discount_rate_value=0.05, volatility=0.20)

    assert process.spot == 100.0
    assert process.discount_rate == 0.05
    assert process.carry_rate == 0.05
    assert process.discount_factor(1.0) == pytest.approx(math.exp(-0.05))
    assert process.underlying_discount_factor(1.0) == pytest.approx(math.exp(-0.05))


def test_black76_process_from_term_structures_is_snapshot() -> None:
    forward = SimpleQuote(100.0)
    process = Black76Process.from_term_structures(
        forward=forward,
        maturity=1.0,
        discount_curve=FlatYieldCurve(rate=0.05),
        volatility=FlatBlackVolatility(0.20),
        strike=100.0,
    )

    forward.value = 101.0

    assert process.forward == 100.0
    assert process.discount_rate_value == 0.05
    assert process.volatility == 0.20


def test_black76_analytic_call_benchmark() -> None:
    result = AnalyticBlackScholesEngine(
        Black76Process(forward=100.0, discount_rate_value=0.05, volatility=0.20)
    ).calculate(make_option(OptionType.CALL))

    assert result.value == pytest.approx(7.5771, abs=1e-4)
    assert result.greeks is not None
    assert result.greeks.delta == pytest.approx(0.5135, abs=1e-4)


def test_black76_analytic_put_benchmark() -> None:
    result = AnalyticBlackScholesEngine(
        Black76Process(forward=100.0, discount_rate_value=0.05, volatility=0.20)
    ).calculate(make_option(OptionType.PUT))

    assert result.value == pytest.approx(7.5771, abs=1e-4)
    assert result.greeks is not None
    assert result.greeks.delta == pytest.approx(-0.4377, abs=1e-4)


def test_black76_process_validation() -> None:
    with pytest.raises(ValueError, match="forward"):
        Black76Process(forward=0.0, discount_rate_value=0.05, volatility=0.20)

    with pytest.raises(ValueError, match="volatility"):
        Black76Process(forward=100.0, discount_rate_value=0.05, volatility=0.0)
