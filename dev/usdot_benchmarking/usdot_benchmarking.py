import jetfuelburn
from jetfuelburn import ureg
from jetfuelburn.statistics import usdot

aircraft = usdot.available_aircraft(2024)


usdot.available_years()
usdot.available_aircraft(usdot.available_years()[0])
result1 = usdot.calculate_fuel_consumption_per_seat(
    year=2024,
    acft="B787-900 Dreamliner",
    R=2000 * ureg.nmi,
)

result2 = usdot.calculate_movements(
    year=2024,
    acft="B787-900 Dreamliner",
)

result3 = usdot.calculate_average_distance(
    year=2024,
    acft="B787-900 Dreamliner",
)

result4 = usdot.calculate_average_time(
    year=2024,
    acft="B787-900 Dreamliner",
)

result5 = usdot.calculate_average_cargo(
    year=2024,
    acft="B787-900 Dreamliner",
)

print(result1)
print(result2)
print(result3)
print(result4)
print(result5)

import jetfuelburn
from jetfuelburn import ureg
from jetfuelburn.reducedorder import seymour_etal

burn = seymour_etal.available_aircraft()[0:140]
