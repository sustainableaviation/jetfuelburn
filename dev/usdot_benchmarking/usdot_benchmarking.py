import jetfuelburn
from jetfuelburn import ureg
from jetfuelburn.statistics import usdot

aircraft = usdot.available_aircraft(2024)

print(aircraft)

usdot.available_years()
usdot.available_aircraft(usdot.available_years()[0])
result = usdot.calculate_fuel_consumption_per_seat(
    year=2024,
    acft="B787-900 Dreamliner",
    R=2000 * ureg.nmi,
)
result2 = usdot.calculate_movements(
    year=2024,
    acft="B787-900 Dreamliner",
)
print(result)
print(result2)
