# Fuel Burn Calculations

```python
import sys
import os

module_path = os.path.abspath("/Users/michaelweinold/github/jetfuelburn")
if module_path not in sys.path:
    sys.path.append(module_path)

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

## Footprint Allocation to Travel Class

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
    )  # Returns: (<Quantity(81.871345, 'kilogram')>, 0, <Quantity(221.052632, 'kilogram')>, 0)

## Fuel Calculation

### Payload-Range Diagram

from jetfuelburn.diagrams import calculate_fuel_consumption_based_on_payload_range

calculate_fuel_consumption_based_on_payload_range(
    d=2000*ureg.nmi,
    oew=142.4*ureg.metric_ton,
    mtow=280*ureg.metric_ton,
    range_point_A=500*ureg.nmi,
    payload_point_B=54*ureg.metric_ton,
    range_point_B=5830*ureg.nmi,
    payload_point_C=25*ureg.metric_ton,
    range_point_C=8575*ureg.nmi,
    range_point_D=9620*ureg.nmi,
)  # Returns: (<Quantity(23527.2045, 'kilogram')>, <Quantity(54000.0, 'kilogram')>)

### Breguet Range Equation

from jetfuelburn.breguet import calculate_fuel_consumption_based_on_breguet_range_equation

calculate_fuel_consumption_based_on_breguet_range_equation(
    R=2000*ureg.nmi,
    LD=18,
    m_after_cruise=100*ureg.metric_ton,
    v_cruise=800*ureg.kph,
    TSFC_cruise=17*(ureg.mg/ureg.N/ureg.s),
)  # Returns: <Quantity(16699.1442, 'kilogram')>

### Reduced-Order Models

from jetfuelburn.reducedorder import (
    yanto_etal,
    lee_etal,
    seymour_etal,
    aim2015
)

#### Yanto et al. (2017-2019)

yanto_etal.available_aircraft()[0:10]  # Returns: ['A318', 'A319', 'A320', 'A321', 'A332', 'A333', 'A342', 'A343', 'A345', 'A346']

yanto_etal.calculate_fuel_consumption(
    acft='A321',
    R=2200*ureg.km,
    PL=18*ureg.metric_ton
)  # Returns: <Quantity(9790.53, 'kilogram')>

#### Lee et al. (2010)

lee_etal.available_aircraft()[0:10]  # Returns: ['A319', 'A320', 'A332', 'AT45', 'B712', 'B732', 'B733', 'B737', 'B738', 'B744']

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
)  # Returns: (<Quantity(15555.2887, 'kilogram')>, <Quantity(5843.11231, 'kilogram')>)

#### AIM2025 (from 2015)

aim2015(
    acft_size_class=8,
    D_climb=300*ureg.km,
    D_cruise=(15000-300-200)*ureg.km,
    D_descent=200*ureg.km,
    PL=55.5*ureg.metric_ton
)  # Returns: <Quantity(117265.491, 'kilogram')>

## Helper Functions (Aerodynamics/Atmospheric Physics)

from jetfuelburn.aux.physics import (
    _calculate_atmospheric_conditions,
    _calculate_aircraft_velocity,   
)

_calculate_atmospheric_conditions(altitude=10000*ureg.m)  # Returns: (<Quantity(0.412715861, 'kilogram / meter ** 3')>, <Quantity(-50.0, 'degree_Celsius')>)

_calculate_aircraft_velocity(
    mach_number=0.8,
    altitude=10000*ureg.m
)  # Returns: <Quantity(862.453921, 'kilometer_per_hour')>