import pytest

from option_pricer import (
    AnalyticBlackScholesEngine,
    Black76Process,
    Commodity,
    CommodityVanillaOption,
    Currency,
    EuropeanExercise,
    OptionType,
    PlainVanillaPayoff,
)


def test_commodity_normalizes_symbol() -> None:
    commodity = Commodity("xau", name="Gold", unit="troy ounce")

    assert commodity.symbol == "XAU"
    assert commodity.name == "Gold"
    assert commodity.unit == "troy ounce"


def test_commodity_rejects_empty_symbol() -> None:
    with pytest.raises(ValueError, match="symbol"):
        Commodity("")


def test_commodity_vanilla_option_validation_and_scaling() -> None:
    option = CommodityVanillaOption(
        commodity=Commodity("XAU", unit="troy ounce"),
        currency=Currency("USD"),
        payoff=PlainVanillaPayoff(OptionType.CALL, strike=2400.0),
        exercise=EuropeanExercise(maturity=1.0),
        quantity=100.0,
    )

    assert option.commodity.symbol == "XAU"
    assert option.currency.code == "USD"
    assert option.notional_value(120.0) == pytest.approx(12_000.0)

    with pytest.raises(ValueError, match="quantity"):
        CommodityVanillaOption(
            commodity=Commodity("XAU"),
            currency=Currency("USD"),
            payoff=PlainVanillaPayoff(OptionType.CALL, strike=2400.0),
            exercise=EuropeanExercise(maturity=1.0),
            quantity=0.0,
        )


def test_commodity_vanilla_option_prices_with_black76_process() -> None:
    option = CommodityVanillaOption(
        commodity=Commodity("XAU", unit="troy ounce"),
        currency=Currency("USD"),
        payoff=PlainVanillaPayoff(OptionType.CALL, strike=2400.0),
        exercise=EuropeanExercise(maturity=1.0),
        quantity=100.0,
    )
    process = Black76Process(forward=2450.0, discount_rate_value=0.04, volatility=0.18)

    result = AnalyticBlackScholesEngine(process).calculate(option)

    assert result.value == pytest.approx(192.1964, abs=1e-4)
    assert option.notional_value(result.value) == pytest.approx(19_219.64, abs=1e-2)
