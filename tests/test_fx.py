import math

import pytest

from option_pricer import (
    AnalyticBlackScholesEngine,
    Currency,
    CurrencyPair,
    EuropeanExercise,
    FlatBlackVolatility,
    FlatYieldCurve,
    GarmanKohlhagenProcess,
    OptionType,
    PlainVanillaPayoff,
    SimpleQuote,
    VanillaOption,
)


def test_currency_normalizes_code() -> None:
    currency = Currency("eur", name="Euro")

    assert currency.code == "EUR"
    assert currency.name == "Euro"


def test_currency_rejects_invalid_code() -> None:
    with pytest.raises(ValueError, match="three-letter"):
        Currency("EURO")


def test_currency_pair_symbol_and_inverse() -> None:
    pair = CurrencyPair(Currency("EUR"), Currency("USD"))

    assert pair.symbol == "EUR/USD"
    assert pair.inverse().symbol == "USD/EUR"


def test_currency_pair_rejects_same_currency() -> None:
    with pytest.raises(ValueError, match="differ"):
        CurrencyPair(Currency("USD"), Currency("usd"))


def test_garman_kohlhagen_helpers() -> None:
    process = GarmanKohlhagenProcess(
        spot=1.10,
        domestic_rate=0.05,
        foreign_rate=0.02,
        volatility=0.12,
        pair=CurrencyPair(Currency("EUR"), Currency("USD")),
    )

    assert process.risk_free_rate == 0.05
    assert process.dividend_yield == 0.02
    assert process.discount_factor(1.0) == pytest.approx(math.exp(-0.05))
    assert process.foreign_discount_factor(1.0) == pytest.approx(math.exp(-0.02))
    assert process.forward(1.0) == pytest.approx(1.10 * math.exp(0.03))


def test_garman_kohlhagen_from_term_structures_is_snapshot() -> None:
    spot = SimpleQuote(1.10)
    process = GarmanKohlhagenProcess.from_term_structures(
        spot=spot,
        maturity=1.0,
        domestic_curve=FlatYieldCurve(rate=0.05),
        foreign_curve=FlatYieldCurve(rate=0.02),
        volatility=FlatBlackVolatility(0.12),
        pair=CurrencyPair(Currency("EUR"), Currency("USD")),
        strike=1.12,
    )

    spot.value = 1.11

    assert process.spot == 1.10
    assert process.domestic_rate == 0.05
    assert process.foreign_rate == 0.02
    assert process.volatility == 0.12


def test_garman_kohlhagen_process_prices_with_existing_analytic_engine() -> None:
    option = VanillaOption(
        payoff=PlainVanillaPayoff(OptionType.CALL, strike=1.12),
        exercise=EuropeanExercise(maturity=1.0),
    )
    process = GarmanKohlhagenProcess(
        spot=1.10,
        domestic_rate=0.05,
        foreign_rate=0.02,
        volatility=0.12,
        pair=CurrencyPair(Currency("EUR"), Currency("USD")),
    )

    result = AnalyticBlackScholesEngine(process).calculate(option)

    assert result.value == pytest.approx(0.057955, abs=1e-6)
    assert result.greeks is not None
    assert result.greeks.delta == pytest.approx(0.552341, abs=1e-6)
