import jetfuelburn
from jetfuelburn import ureg
from jetfuelburn.statistics import usdot

aircraft = usdot.available_aircraft(2024)


usdot.available_years()
usdot.available_aircraft(usdot.available_years()[0])
result1 = usdot.calculate_fuel_consumption_per_seat(
    year=2024,
    acft="Boeing 777-200ER/200LR/233LR",
    R= 6187 * ureg.km,
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
    acft="Boeing 777-200ER/200LR/233LR",
)

result7 = result1 * result6

print(result1)
print(result2)
print(result3)
print(result4)
print(result5)
print(result6)
print(result7)

