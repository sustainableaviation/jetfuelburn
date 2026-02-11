# %%
import csv
import jetfuelburn
from jetfuelburn import ureg

from jetfuelburn.statistics import usdot

list_range = [r for r in range(125, 1000, 40)]

list_data_A320 = [
    usdot.calculate_fuel_consumption_per_seat(
        year=2018, acft="Airbus Industrie A320-200n", R=range * ureg.km
    ).magnitude
    for range in list_range
]
list_data_B737 = [
    usdot.calculate_fuel_consumption_per_seat(
        year=2018, acft="Boeing 737-800", R=range * ureg.km
    ).magnitude
    for range in list_range
]
list_data_A330 = [
    usdot.calculate_fuel_consumption_per_seat(
        year=2018, acft="Airbus Industrie A330-200", R=range * ureg.km
    ).magnitude
    for range in list_range
]
list_data_B757 = [
    usdot.calculate_fuel_consumption_per_seat(
        year=2018, acft="Boeing 757-200", R=range * ureg.km
    ).magnitude
    for range in list_range
]
list_data_A350 = [
    usdot.calculate_fuel_consumption_per_seat(
        year=2018, acft="Airbus Industrie A350-900", R=range * ureg.km
    ).magnitude
    for range in list_range
]
list_data_B787 = [
    usdot.calculate_fuel_consumption_per_seat(
        year=2018, acft="B787-900 Dreamliner", R=range * ureg.km
    ).magnitude
    for range in list_range
]

with open(
    "/Users/michaelweinold/github/jetfuelburn/dev/homepage/usdot_fuel_burn.csv",
    mode="w",
    newline="",
) as file:
    writer = csv.writer(file)
    writer.writerow(["Range (km)", "A320", "B737", "A330", "B757", "A350", "B787"])
    for i, range_value in enumerate(list_range):
        writer.writerow(
            [
                range_value,
                list_data_A320[i],
                list_data_B737[i],
                list_data_A330[i],
                list_data_B757[i],
                list_data_A350[i],
                list_data_B787[i],
            ]
        )
