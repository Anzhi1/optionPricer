from datetime import date

from option_pricer import (
    Actual365Fixed,
    BusinessDayConvention,
    DiscountingSwapEngine,
    FlatForwardRateCurve,
    FlatYieldCurve,
    Frequency,
    IborIndex,
    NullCalendar,
    SwapType,
    VanillaInterestRateSwap,
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

swap = VanillaInterestRateSwap(
    swap_type=SwapType.PAYER,
    notional=1_000_000.0,
    fixed_rate=0.05,
    fixed_schedule=schedule,
    fixed_day_count=day_count,
    floating_schedule=schedule,
    index=index,
    spread=0.001,
)

discount_curve = FlatYieldCurve(
    rate=0.05,
    reference_date=valuation_date,
    day_count=day_count,
)

result = DiscountingSwapEngine(discount_curve).calculate(swap)

print(f"fixed leg pv: {result.diagnostics['fixed_leg_pv']:.2f}")
print(f"floating leg pv: {result.diagnostics['floating_leg_pv']:.2f}")
print(f"fair rate: {result.diagnostics['fair_rate']:.4%}")
print(f"value: {result.value:.2f}")
