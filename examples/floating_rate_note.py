from datetime import date

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    DiscountingBondEngine,
    FlatForwardRateCurve,
    FlatYieldCurve,
    FloatingRateNote,
    Frequency,
    IborIndex,
    NullCalendar,
    generate_schedule,
)

valuation_date = date(2026, 1, 15)
day_count = Actual365Fixed()

schedule = generate_schedule(
    start_date=valuation_date,
    end_date=date(2028, 1, 15),
    frequency=Frequency.ANNUAL,
    calendar=NullCalendar(),
    business_day_convention=BusinessDayConvention.UNADJUSTED,
)

projection_curve = FlatForwardRateCurve(
    rate=0.04,
    reference_date=valuation_date,
    day_count=day_count,
)

index = IborIndex(
    name="USD-TEST-12M",
    tenor_months=12,
    day_count=day_count,
    fixing_calendar=NullCalendar(),
    business_day_convention=BusinessDayConvention.UNADJUSTED,
    projection_curve=projection_curve,
)

note = FloatingRateNote(
    notional=1_000_000.0,
    spread=0.001,
    schedule=schedule,
    index=index,
)

discount_curve = FlatYieldCurve(
    rate=0.05,
    reference_date=valuation_date,
    day_count=day_count,
)

result = DiscountingBondEngine(discount_curve).calculate(note)

print(f"cashflows: {len(note.cashflows())}")
print(f"value: {result.value:.2f}")
