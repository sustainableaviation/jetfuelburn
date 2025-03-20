# Fuel Burn Calculations

## Breguet Range Equation

Using the Breguet range equation is perhaps the most well-known approach to computing the range of an aircraft.
Of course, the equation can also be solved for the fuel required to fly a given distance.

While mass-after-cruise and range are straightforward inputs,
the lift-to-drag ratio (L/D) and specific fuel consumption (TSFC) are often more difficult to obtain.

!!! note
    First, we import the `jetfuelburn` package and the `pint` package unit registry. \
    All code editors on this page will remember these imports and later variable definitions.

```pyodide session='fuel' install='jetfuelburn'
import jetfuelburn
from jetfuelburn import ureg
from jetfuelburn.breguet import calculate_fuel_consumption_range_equation

calculate_fuel_consumption_range_equation(
    R=2000*ureg.nmi,
    LD=18,
    m_after_cruise=100*ureg.metric_ton,
    v_cruise=800*ureg.kph,
    TSFC_cruise=17*(ureg.mg/ureg.N/ureg.s),
)
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.breguet.calculate_fuel_consumption_range_equation`][]


## Payload/Range Diagrams

Using payload/range diagrams is another common method for calculating fuel burn of aircraft.
This method is particularly popular due to the excellent data availability. After all, the payload/range diagram is a standard feature of aircraft performance manuals.

```pyodide session='fuel'
from jetfuelburn.diagrams import calculate_fuel_consumption_payload_range

calculate_fuel_consumption_payload_range(
    d=2000*ureg.nmi,
    oew=142.4*ureg.metric_ton,
    mtow=280*ureg.metric_ton,
    range_point_A=500*ureg.nmi,
    payload_point_B=54*ureg.metric_ton,
    range_point_B=5830*ureg.nmi,
    payload_point_C=25*ureg.metric_ton,
    range_point_C=8575*ureg.nmi,
    range_point_D=9620*ureg.nmi,
)
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.diagrams.calculate_fuel_consumption_payload_range`][]

## Reduced-Order Models

Both the range equation and payload/range diagrams cannot capture the full complexity of fuel burn calculations.
For example, they do not explicitly consider the impact of climb/descent phases. This is why researchers have developed _reduced order models_.

These models are based on detailed simulations, using eg. the [EUROCONTROL BADA](https://www.eurocontrol.int/model/bada) or [Piano X](https://www.lissys.uk/index2.html) software.
Both are physics-based models that simulate the fuel-burn of aircraft depending on its flight profile. All reduced-order models used these high-resolution models to compute many data points and then fit a simplified (=reduced order) model to these data points. Some reduced order models have only one variable (eg. range), while others have more (eg. range, payload, altitude, etc.).

!!! note
    Currently, the `jetfuelburn` package includes reduced-order models from:

     - [Yanto et al. (2017/2019)](https://doi.org/10.2514/6.2017-3338)
     - [Lee et al. (2010)](https://doi.org/10.2514/6.2010-9156)
     - [Seymour et al. (2019) "FEAT Model"](https://doi.org/10.1016/j.trd.2020.102528)
     - [Drey et al. (2015) "AIM215 Model"](https://doi.org/10.1016/j.tranpol.2019.04.013)

#### Yanto et al. (2017-2019)

Reduced-order models always offer multiple aircraft, for which simulations were run. The `available_aircraft` function always returns a list of these aircraft.

```pyodide session='fuel'
from jetfuelburn.reducedorder import yanto_etal
yanto_etal.available_aircraft()[0:10]
```

Fuel consumption calculations are then performed using the `calculate_fuel_consumption` function.

```pyodide session='fuel'
yanto_etal.calculate_fuel_consumption(
    acft='A321',
    R=2200*ureg.km,
    PL=18*ureg.metric_ton
)
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.reducedorder.yanto_etal`][]

#### Seymour et al. (2019)

!!! warning
    Note that Seymour et al. use "average weights" for every aircraft.
    The only variable input is therefore the aircraft range.

```pyodide session='fuel'
from jetfuelburn.reducedorder import seymour_etal
seymour_etal.calculate_fuel_consumption(
    acft='A321',
    R=2200*ureg.km,
)
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.reducedorder.seymour_etal`][]

#### Lee et al. (2010)

!!! warning
    Note that Lee et al. use weight [N] instead of mass [kg] as input.

```pyodide session='fuel'
from jetfuelburn.reducedorder import lee_etal
lee_etal.calculate_fuel_consumption(
    acft='B732',
    W_E=265825*ureg.N,
    W_MPLD=156476*ureg.N,
    W_MTO=513422*ureg.N,
    W_MF=142365*ureg.N,
    S=91.09*ureg.m ** 2,
    C_D0=0.0214,
    C_D2=0.0462,
    c=(2.131E-4)/ureg.s,
    h=9144*ureg.m,
    V=807.65*ureg.kph,
    d=2000*ureg.nmi
)
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.reducedorder.lee_etal`][]

#### AIM2025 (from 2015)

!!! warning
    Note that the AIM2015 model uses 'representative' aircraft (in different size classes) instead of specific aircraft types.
    See the function documentation for a list of available size classes.

```pyodide session='fuel'
from jetfuelburn.reducedorder import aim2015
aim2015.calculate_fuel_consumption(
    acft_size_class=8,
    D_climb=300*ureg.km,
    D_cruise=(15000-300-200)*ureg.km,
    D_descent=200*ureg.km,
    PL=55.5*ureg.metric_ton
)
```

!!! note
    For additional information, compare the function documentation:
    [`jetfuelburn.reducedorder.aim2015`][]


## Helper Functions (Aerodynamics/Atmospheric Physics)

The `jetfuelburn` package also includes helper functions for basic atmospheric physics problems.
Some reduced-order models call these internally - but they can also be used independently.

```pyodide session='fuel'
from jetfuelburn.aux.physics import (
    _calculate_atmospheric_conditions,
    _calculate_aircraft_velocity,   
)
_calculate_aircraft_velocity(
    mach_number=0.8,
    altitude=10000*ureg.m
)
```

and

```pyodide session='fuel'
_calculate_atmospheric_conditions(altitude=10000*ureg.m)
```