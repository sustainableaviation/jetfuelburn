import jetfuelburn
from jetfuelburn.reducedorder import sacchi_etal, myclimate
from figures.reduced_order.reduced_order_sacchi_weight import pax_max
from jetfuelburn import ureg
from jetfuelburn.statistics import usdot
from jetfuelburn.reducedorder import aim2015

aircraft = usdot.available_aircraft(2024)

result10 = myclimate.available_aircraft()

usdot.available_years()
usdot.available_aircraft(usdot.available_years()[0])
result1 = usdot.calculate_fuel_consumption_per_seat(
    year=2024,
    acft="Boeing 777-200ER/200LR/233LR",
    R=6187 * ureg.km,
)

result2 = usdot.calculate_movements(
    year=2024,
    acft="Boeing 777-200ER/200LR/233LR",
)

result3 = usdot.calculate_average_distance(
    year=2024,
    acft="Boeing 777-200ER/200LR/233LR",
)

result4 = usdot.calculate_average_time(
    year=2024,
    acft="Boeing 777-200ER/200LR/233LR",
)

result5 = usdot.calculate_average_cargo(
    year=2024,
    acft="Boeing 777-200ER/200LR/233LR",
)

result6 = usdot.calculate_average_pax(
    year=2024,
    acft="Canadair CRJ 900",
)

result7 = result1 * result6

result8 = usdot.calculate_total_fuel_consumption(
    year=2024,
)

fuelburn1 = sacchi_etal.calculate_fuel_consumption(
    year=2024, pax_max=180, pax=160, R=1500 * ureg.km
)

fuelburn2 = sacchi_etal.calculate_fuel_consumption(
    year=2024, pax_max=180, pax=120, R=1500 * ureg.km
)


print(fuelburn1)
print(fuelburn2)
print(result6)

print(result10)
