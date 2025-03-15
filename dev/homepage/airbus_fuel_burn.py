# %%
import csv
import jetfuelburn
from jetfuelburn import ureg

from jetfuelburn.reducedorder import seymour_etal

list_range = [r for r in range(1, 8000, 40)]

list_data_a320 = [
    seymour_etal.calculate_fuel_consumption(
        acft='A320',
        R=range * ureg.km
    ).magnitude for range in list_range
]
list_data_a380 = [
    seymour_etal.calculate_fuel_consumption(
        acft='A388',
        R=range * ureg.km
    ).magnitude for range in list_range
]
list_data_a330 = [
    seymour_etal.calculate_fuel_consumption(
        acft='A333',
        R=range * ureg.km
    ).magnitude for range in list_range
]
list_data_a340 = [
    seymour_etal.calculate_fuel_consumption(
        acft='A343',
        R=range * ureg.km
    ).magnitude for range in list_range
]
list_data_a350 = [
    seymour_etal.calculate_fuel_consumption(
        acft='A359',
        R=range * ureg.km
    ).magnitude for range in list_range
]

with open('/Users/michaelweinold/github/jetfuelburn/dev/homepage/airbus_fuel_burn.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Range (km)', 'A320', 'A388', 'A333', 'A343', 'A359'])
    for i, range_value in enumerate(list_range):
        writer.writerow([
            range_value,
            list_data_a320[i],
            list_data_a380[i],
            list_data_a330[i],
            list_data_a340[i],
            list_data_a350[i]
        ])