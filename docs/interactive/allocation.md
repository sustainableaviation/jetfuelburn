# Cabin Class Fuel Burn Allocation

Passengers in first class are allocated more fuel than passengers in economy class. This is because first class seats are larger and heavier than economy class seats. The fuel burn allocation implemented in JetFuelBurn is calculated based on the area of the cabin class seats. This follows current recommendations of both ICAO and IATA.

!!! info

    For a detailed discussion on area and weight considerations, compare World Bank Policy Research Working Paper 6471 (2013) by Bofinger and Strand ["Calculating the carbon footprint from different classes of air travel."](https://hdl.handle.net/10986/15602).

```pyodide session="allocation" install="jetfuelburn"
from jetfuelburn import ureg
from jetfuelburn.aux.allocation import footprint_allocation_by_area
footprint_allocation_by_area(
        fuel_per_flight=14000*ureg.kg,
        size_factor_eco=1,
        size_factor_premiumeco=0,
        size_factor_business=1.5,
        size_factor_first=0,
        seats_eco=154,
        seats_premiumeco=0,
        seats_business=24,
        seats_first=0,
        load_factor_eco=0.9,
        load_factor_premiumeco=0,
        load_factor_business=0.5,
        load_factor_first=0,
    )
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.aux.allocation.footprint_allocation_by_area`][]