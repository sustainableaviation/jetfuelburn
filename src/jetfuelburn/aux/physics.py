import math
from jetfuelburn import ureg


@ureg.check(
    '[length]' # altitude
)
def _calculate_atmospheric_conditions(altitude: float) -> dict[float, float]:
    r"""
    Computes the air density and temperature as a function of altitute, for altitudes up to 20,000 meters.

    All calculations are based on the ISA (International Standard Atmosphere):

    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a8/International_Standard_Atmosphere.svg" width="250">

    Temperature in the Troposphere is calculated according to:

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
    [`atmos()` in `openap/extra/aero.py`](https://github.com/TUDelft-CNS-ATM/openap/blob/39619977962fe6b4a86ab7efbefa70890eecfe36/openap/extra/aero.py#L48C5-L48C10)
    by [Junzi Sun](https://github.com/junzis). Note that `jetfuelburn` function has been re-written completely and does not build on the `openap` code.

    References
    --------
    - Temperature: [Eqn.(1.6) in Sadraey (2nd Edition, 2024)](https://doi.org/10.1201/9781003279068)
    - [Density Equations on Wikipedia](https://en.wikipedia.org/wiki/Barometric_formula#Density_equations)

    Returns
    -------
    dict
        'density' : ureg.Quantity
            Air density [kg/m³]
        'temperature' : ureg.Quantity
            Air temperature [°C]

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.aux.physics import _calculate_atmospheric_conditions
    _calculate_atmospheric_conditions(altitude=10000*ureg.m)
    ```
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
        rho = rho_1 * math.exp(-g * M * (altitude - 11000 * ureg.m) / (R * temperature_lower_stratosphere))

    return {
        'density': rho.to(ureg.kg/ureg.m ** 3),
        'temperature': temperature.to(ureg.celsius)
    }

@ureg.check(
    '[speed]',
    '[length]'
)
def _calculate_dynamic_pressure(
    speed: float,
    altitude: float
) -> float:
    r"""
    Computes the dynamic pressure $q$ at a given speed and altitude.

    $$
    q = \frac{1}{2} \rho V^2
    $$

    where:

    | Symbol | Dimension       | Description         |
    |--------|-----------------|---------------------|
    | $q$    | [pressure]      | dynamic pressure    |
    | $\rho$ | [mass/volume]   | air density         |
    | $V$    | [speed]         | aircraft speed      |


    References
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

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.aux.physics import _calculate_dynamic_pressure
    _calculate_dynamic_pressure(
        speed=833*ureg.kph,
        altitude=10000*ureg.m
    )
    ```
    """
    air_density = _calculate_atmospheric_conditions(altitude)['density']
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
    r"""
    Converts aircraft speed from mach number $M$ to airspeed $V$,
    depending on the flight altitude $h$.

    $$
        V = M \sqrt{\gamma R T(h)}
    $$

    where:

    | Symbol   | Dimension       | Value           | Description                   |
    |----------|-----------------|-----------------|-------------------------------|
    | $V$      | [speed]         | variable        | aircraft speed                |
    | $M$      | [dimensionless] | variable        | Mach number                   |
    | $\gamma$ | [dimensionless] | 1.4             | ratio of specific heat (air)  |
    | $R$      | (complicated)   | 287 J/(kg*K)    | specific gas constant for air |

    Parameters
    ----------
    mach_number : float [dimensionless]
        Mach number
    altitude : float [length]
        Flight altitude above sea level

    References
    --------
    - [Mach Number on Wikipedia](https://en.wikipedia.org/wiki/Mach_number#Calculation)
    - [Eqn.(1.33)-(1.34) in Sadraey (2nd Edition, 2024)](https://doi.org/10.1201/9781003279068)

    Returns
    -------
    float
        Aircraft velocity [km/h]

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.aux.physics import _calculate_aircraft_velocity
    _calculate_aircraft_velocity(
        mach_number=0.8,
        altitude=10000*ureg.m
    )
    ```
    """

    temperature = _calculate_atmospheric_conditions(altitude)['temperature']

    R = 287.052874 * (ureg.J/(ureg.kg*ureg.K)) # specific gas constant for air 
    gamma = 1.4 * ureg.dimensionless # ratio of specific heat for air
    velocity = mach_number * (gamma * R * temperature.to(ureg.K)) ** 0.5

    return velocity.to(ureg.kph)