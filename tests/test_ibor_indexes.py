from datetime import date

import pytest

from option_pricer import (
    Actual360,
    BusinessDayConvention,
    FlatForwardRateCurve,
    IborIndex,
    WeekendCalendar,
)


def test_ibor_index_projects_rate_from_forward_rate_curve() -> None:
    index = IborIndex(
        name="USD-SOFR-3M",
        tenor_months=3,
        day_count=Actual360(),
        fixing_calendar=WeekendCalendar(),
        business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
        projection_curve=FlatForwardRateCurve(
            rate=0.042,
            reference_date=date(2026, 1, 15),
            day_count=Actual360(),
        ),
    )

    assert index.rate(date(2026, 1, 15), date(2026, 4, 15)) == 0.042


def test_ibor_index_adjusts_fixing_date() -> None:
    index = IborIndex(
        name="USD-SOFR-3M",
        tenor_months=3,
        day_count=Actual360(),
        fixing_calendar=WeekendCalendar(),
        business_day_convention=BusinessDayConvention.FOLLOWING,
        projection_curve=FlatForwardRateCurve(rate=0.042),
    )

    assert index.fixing_date(date(2026, 1, 17)) == date(2026, 1, 19)


def test_ibor_index_rejects_invalid_tenor() -> None:
    with pytest.raises(ValueError, match="tenor_months"):
        IborIndex(
            name="USD-SOFR-3M",
            tenor_months=0,
            day_count=Actual360(),
            fixing_calendar=WeekendCalendar(),
            business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
            projection_curve=FlatForwardRateCurve(rate=0.042),
        )
