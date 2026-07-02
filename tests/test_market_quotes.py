import pytest

from option_pricer import SimpleQuote


def test_simple_quote_stores_finite_value() -> None:
    quote = SimpleQuote(100.0)

    assert quote.value == 100.0


def test_simple_quote_can_be_updated_explicitly() -> None:
    quote = SimpleQuote(100.0)

    quote.value = 101.25

    assert quote.value == 101.25


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_simple_quote_rejects_non_finite_values(bad_value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        SimpleQuote(bad_value)

    quote = SimpleQuote(100.0)
    with pytest.raises(ValueError, match="finite"):
        quote.value = bad_value
