import pytest

from option_pricer import (
    AnalyticBlackScholesEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
    VanillaOption,
)


def make_process() -> BlackScholesMertonProcess:
    return BlackScholesMertonProcess(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )


def make_option(option_type: OptionType) -> VanillaOption:
    return VanillaOption(
        payoff=PlainVanillaPayoff(option_type, strike=100.0),
        exercise=EuropeanExercise(maturity=1.0),
    )


def test_analytic_black_scholes_call_benchmark() -> None:
    result = AnalyticBlackScholesEngine(make_process()).calculate(make_option(OptionType.CALL))

    assert result.value == pytest.approx(10.4506, abs=1e-4)
    assert result.greeks is not None
    assert result.greeks.delta == pytest.approx(0.6368, abs=1e-4)
    assert result.greeks.gamma == pytest.approx(0.0188, abs=1e-4)
    assert result.greeks.vega == pytest.approx(37.5240, abs=1e-4)
    assert result.greeks.theta == pytest.approx(-6.4140, abs=1e-4)
    assert result.greeks.rho == pytest.approx(53.2325, abs=1e-4)


def test_analytic_black_scholes_put_benchmark() -> None:
    result = AnalyticBlackScholesEngine(make_process()).calculate(make_option(OptionType.PUT))

    assert result.value == pytest.approx(5.5735, abs=1e-4)
    assert result.greeks is not None
    assert result.greeks.delta == pytest.approx(-0.3632, abs=1e-4)
    assert result.greeks.gamma == pytest.approx(0.0188, abs=1e-4)
    assert result.greeks.vega == pytest.approx(37.5240, abs=1e-4)
    assert result.greeks.theta == pytest.approx(-1.6579, abs=1e-4)
    assert result.greeks.rho == pytest.approx(-41.8905, abs=1e-4)
