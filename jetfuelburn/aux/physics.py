# %%

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-ureg-registry

import numpy as np

@ureg.check(
    '[length]' # altitude
)
def _calculate_atmospheric_conditions(altitude: float) -> tuple[float, float]:
    """
    Computes the air density and temperature as a function of altitute, for altitudes up to 20,000 meters.

    All calculations are based on the ISA (International Standard Atmosphere):

    .. image:: https://upload.wikimedia.org/wikipedia/commons/6/62/Comparison_International_Standard_Atmosphere_space_diving.svg

    Temperature in the Troposphere is calculated using the following formula:

    $$
    T=T_0 - L * h
    $$

    in the lower Stratosphere, it is simply -56.5°C.

    where:

    | Symbol | Dimension             | Description                         | Value        |
    |--------|-----------------------|-------------------------------------|--------------|
    | $T$    | [temperature]         | temperature at altitude $h$         | N/A          |
    | $T_0$  | [temperature]         | temperature at sea level            | 288.15 K     |
    | $L$    | [temperature/length]  | temperature lapse rate (Troposphere)| 0.0065 K/m   |
    | $h$    | [length]              | altitude                            | N/A          |

    Density is calculated using the _exponential approximation_:

    $$
    \rho = \rho_0 * e^{-\frac{g*h}{R*T}}
    $$

    where:

    | Symbol  | Dimension             | Description                         | Value        |
    |---------|-----------------------|-------------------------------------|--------------|
    | $\rho$  | [mass/volume]         | air density at altitude $h$         | N/A          |
    | $\rho_0$| [mass/volume]         | air density at sea level            | 1.225 kg/m³  |
    | $g$     | [acceleration]        | acceleration due to gravity         | 9.80665 m/s² |
    | $R$     | [specific gas constant| specific gas constant for air       | 287 J/(kg*K) |
    | $T$     | [temperature]         | temperature at altitude $h$         | N/A          |

    Parameters
    ----------
    altitude : float [distance]
        Altitude above sea level

    Notes
    -----
    Compare also the function
    [`atmos()` in openap/extra/aero.py](https://github.com/TUDelft-CNS-ATM/openap/blob/39619977962fe6b4a86ab7efbefa70890eecfe36/openap/extra/aero.py#L48C5-L48C10)
    by Junzi Sun (https://github.com/junzis).
    Note that the present function has been re-written completely.

    See Also
    --------
    - Temperature: [Eqn. (1.6) in Sadraey (2nd Edition, 2024)](https://doi.org/10.1201/9781003279068)
    - [Density Equations on Wikipedia](https://en.wikipedia.org/wiki/Barometric_formula#Density_equations)

    Returns
    -------
    tuple[float, float]
        Tuple of air density (⍴)[kg/m³], temperature [°C]
    """
    if altitude < 0 * ureg.m:
        raise ValueError("Altitude must not be <0.")
    elif altitude > 20000 * ureg.m:
        raise ValueError("Altitude must not be >20000. We are not considering the stratosphere.")

    temperature_0 = 288.15 * ureg.K # sea-level standard tempreature
    lapse_rate = 0.0065 * (ureg.K/ureg.m) # temperature lapse rate in the troposphere
    temperature_lower_stratosphere = 216.65 * ureg.K # constant temperature in the lower stratosphere
    rho_0 = 1.225 * (ureg.kg/ureg.m ** 3) # sea-level standard atmospheric density
    rho_1 = 0.36391 * (ureg.kg/ureg.m ** 3) # density at 11000 meters
    g = 9.80665 * (ureg.m/ureg.s ** 2) # acceleration due to gravity
    R = 8.3144598 * ((ureg.N * ureg.m)/(ureg.mol*ureg.K)) # univeral gas constant
    M = 0.0289644 * ureg.kg/ureg.mol # molar mass of dry air

    if altitude <= 11000 * ureg.m:
        temperature = temperature_0 - lapse_rate * altitude.to(ureg.m)
        rho = rho_0 * ((temperature_0 - lapse_rate * altitude) / temperature_0) ** (((g * M) / (R * lapse_rate)) - 1)
    else:
        temperature = temperature_lower_stratosphere
        rho = rho_1 * np.exp(-g * M * (altitude - 11000 * ureg.m) / (R * temperature_lower_stratosphere))

    return rho.to(ureg.kg/ureg.m ** 3), temperature.to(ureg.celsius)


@ureg.check(
    '[speed]',
    '[length]'
)
def _calculate_dynamic_pressure(
    speed: float,
    altitude: float
) -> float:
    """
    Computes the dynamic pressure at a given speed and altitude.

    See Also
    --------
    - [Dynamic Pressure on Wikipedia](https://en.wikipedia.org/wiki/Dynamic_pressure)
    - [Eqn.(2.63) in Young (2018)](https://doi.org/10.1002/9781118534786)

    Parameters
    ----------
    speed : float
        Aircraft speed [speed]
    altitude : float
        Aircraft altitude above sea level [distance]

    Returns
    -------
    float
        Dynamic pressure [Pa]
        
    """
    air_density = _calculate_atmospheric_conditions(altitude)[0]
    dynamic_pressure = 0.5 * air_density * speed ** 2
    return dynamic_pressure.to(ureg.Pa)


@ureg.check(
    '[]', # mach number is dimensionless
    '[length]' # altitude
)
def _calculate_aircraft_velocity(
    mach_number: float,
    altitude: float
) -> float:
    """
    Converts aircraft speed from mach number to kilometers per hour,
    depending on the flight altitude air temperature.

    Parameters
    ----------
    mach : float [dimensionless]
        Mach number
    temperature : float [temperature]
        Temperature at flight altitute (OAT)

    See Also
    --------
    - Velocity: [Mach Number Calculation](https://en.wikipedia.org/wiki/Mach_number#Calculation)

    Returns
    -------
    float
        Aircraft velocity [km/h]
    """

    temperature = _calculate_atmospheric_conditions(altitude)[1]

    R = 287.052874 * (ureg.J/(ureg.kg*ureg.K)) # specific gas constant for air 
    gamma = 1.4 * ureg.dimensionless # ratio of specific heat for air
    velocity = mach_number * np.sqrt(gamma*R*temperature.to(ureg.K))

    return velocity.to(ureg.kph)