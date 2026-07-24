from datetime import date

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    DiscountingBondEngine,
    FixedRateBond,
    FlatYieldCurve,
    Frequency,
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

bond = FixedRateBond(
    notional=1_000_000.0,
    fixed_rate=0.05,
    schedule=schedule,
    day_count=day_count,
)

discount_curve = FlatYieldCurve(
    rate=0.05,
    reference_date=valuation_date,
    day_count=day_count,
)

result = DiscountingBondEngine(discount_curve).calculate(bond)

print(f"cashflows: {len(bond.cashflows())}")
print(f"value: {result.value:.2f}")
