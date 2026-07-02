import pytest

np = pytest.importorskip("numpy")

from option_pricer import (  # noqa: E402
    AnalyticBlackScholesEngine,
    BlackScholesMertonProcess,
    EuropeanExercise,
    EuropeanMonteCarloEngine,
    OptionType,
    PlainVanillaPayoff,
    VanillaOption,
)


def make_process() -> BlackScholesMertonProcess:
    return BlackScholesMertonProcess(100.0, 0.05, 0.0, 0.20)


def make_call() -> VanillaOption:
    return VanillaOption(
        payoff=PlainVanillaPayoff(OptionType.CALL, 100.0),
        exercise=EuropeanExercise(1.0),
    )


def test_monte_carlo_is_reproducible_with_fixed_seed() -> None:
    process = make_process()
    option = make_call()

    first = EuropeanMonteCarloEngine(process, paths=20_000, seed=42).calculate(option)
    second = EuropeanMonteCarloEngine(process, paths=20_000, seed=42).calculate(option)

    assert first.value == second.value
    assert first.diagnostics is not None
    assert first.diagnostics["seed"] == 42


def test_monte_carlo_call_is_close_to_analytic_value() -> None:
    process = make_process()
    option = make_call()

    analytic = AnalyticBlackScholesEngine(process).calculate(option).value
    result = EuropeanMonteCarloEngine(process, paths=100_000, seed=7).calculate(option)

    assert result.value == pytest.approx(analytic, abs=0.15)
    assert result.diagnostics is not None
    assert result.diagnostics["standard_error"] > 0.0


def test_monte_carlo_antithetic_records_diagnostics() -> None:
    result = EuropeanMonteCarloEngine(
        make_process(),
        paths=20_000,
        seed=7,
        antithetic=True,
    ).calculate(make_call())

    assert result.value > 0.0
    assert result.diagnostics is not None
    assert result.diagnostics["paths"] == 20_000
    assert result.diagnostics["antithetic"] is True
    assert result.diagnostics["standard_error"] > 0.0


def test_monte_carlo_antithetic_requires_even_paths() -> None:
    with pytest.raises(ValueError, match="paths must be even"):
        EuropeanMonteCarloEngine(make_process(), paths=101, antithetic=True)
