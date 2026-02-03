# %%
import math
from jetfuelburn import ureg


@ureg.check('[length]')
def _calculate_atmospheric_temperature(altitude):
    r"""
    Computes the air temperature as a function of altitude up to 20,000 meters 
    based on the International Standard Atmosphere (ISA):

    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a8/International_Standard_Atmosphere.svg" width="250">
    
    Temperature in the Troposphere (<= 11,000 m) is calculated according to
    
    $$
    T = T_0 - L \cdot h
    $$

    where:

    | Symbol | Dimension             | Description                         | Value        |
    |--------|-----------------------|-------------------------------------|--------------|
    | $T$    | [temperature]         | temperature at altitude $h$         | N/A          |
    | $T_0$  | [temperature]         | temperature at sea level            | 288.15 K     |
    | $L$    | [temperature/length]  | temperature lapse rate (Troposphere)| 0.0065 K/m   |

    Temperature in the lower Stratosphere (> 11,000 m) is assumed constant at -56.5°C (216.65 K).

    References
    ----------
    Eqn.(1.6) in Sadraey, M. H. (2017). Aircraft Performance: An Engineering Approach . _CRC Press_. doi:[10.1201/9781003279068](https://doi.org/10.1201/9781003279068)

    Parameters
    ----------
    altitude : Quantity [length]
        Altitude above sea level (0 to 20,000 meters).

    Returns
    -------
    ureg.Quantity (float) [temperature]
        Air temperature (°C).

    Raises
    ------
    ValueError
        If altitude is less than 0 m or greater than 20,000 m.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.utility.physics import _calculate_atmospheric_temperature
    _calculate_atmospheric_temperature(altitude=10000*ureg.m)
    ```
    """
    if altitude < 0 * ureg.m:
        raise ValueError("Altitude must not be < 0.")
    elif altitude > 20000 * ureg.m:
        raise ValueError("Altitude must not be > 20000 m.")

    temperature_0 = 288.15 * ureg.K            # Sea-level standard temperature
    lapse_rate = 0.0065 * (ureg.K / ureg.m)    # Temperature lapse rate
    temperature_stratosphere = 216.65 * ureg.K # Constant temp in lower stratosphere

    if altitude <= 11000 * ureg.m:
        temperature = temperature_0 - lapse_rate * altitude
    else:
        temperature = temperature_stratosphere

    return temperature.to(ureg.celsius)


@ureg.check('[length]')
def _calculate_atmospheric_density(altitude):
    r"""
    Computes the air density as a function of altitude up to 20,000 meters 
    based on the International Standard Atmosphere (ISA):

    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a8/International_Standard_Atmosphere.svg" width="250">

    Density in the Troposphere (<= 11,000 m) is calculated according to

    $$
    \rho = \rho_0 \left( \frac{T}{T_0} \right)^{\frac{-g}{L R} - 1}
    $$

    Temperature in the lower Stratosphere (> 11,000 m) is calculated according to

    $$
    \rho = \rho_1 e^{\frac{-g M (h - h_1)}{R T_s}}
    $$

    where:

    | Symbol  | Dimension                   | Description                                | Value                |
    |---------|-----------------------------|--------------------------------------------|----------------------|
    | $\rho$  | [mass/volume]               | air density at altitude $h$                | N/A                  |
    | $\rho_0$| [mass/volume]               | air density at sea level                   | 1.225 kg/m³          |
    | $\rho_1$| [mass/volume]               | air density at tropopause (11,000 m)       | 0.36391 kg/m³        |
    | $T$     | [temperature]               | temperature at altitude $h$                | N/A                  |
    | $T_0$   | [temperature]               | temperature at sea level                   | 288.15 K             |
    | $T_s$   | [temperature]               | constant temperature in lower Stratosphere | 216.65 K             |
    | $h$     | [length]                    | altitude above sea level                   | variable             |
    | $h_1$   | [length]                    | altitude at tropopause                     | 11,000 m             |
    | $g$     | [length/time²]              | acceleration due to gravity                | 9.80665 m/s²         |
    | $L$     | [temperature/length]        | temperature lapse rate (Troposphere)       | 0.0065 K/m           |
    | $R$     | [energy/(mass*temperature)] | specific gas constant for air              | 287.052874 J/(kg·K)  |
    | $M$     | [mass/mole]                 | molar mass of dry air                      | 0.0289644 kg/mol     |

    References
    ----------
    - Troposphere: Eqn. (4.14) in Young, T. M. (2018). Performance of the Jet Transport Airplane. _John Wiley & Sons_. doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)
    - Stratosphere: Eqn. (4.16) in Young, T. M. (2018). Performance of the Jet Transport Airplane. _John Wiley & Sons_. doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

    Parameters
    ----------
    altitude : Quantity [length]
        Altitude above sea level (0 to 20,000 meters).

    Returns
    -------
    ureg.Quantity (float) [mass/volume]
        Air density (kg/m³).

    Raises
    ------
    ValueError
        If altitude is less than 0 m or greater than 20,000 m.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.utility.physics import _calculate_atmospheric_density
    _calculate_atmospheric_density(altitude=10000*ureg.m)
    ```
    """
    if altitude < 0 * ureg.m:
        raise ValueError("Altitude must not be < 0.")
    elif altitude > 20000 * ureg.m:
        raise ValueError("Altitude must not be > 20000 m.")

    rho_0 = 1.225 * (ureg.kg / ureg.m**3)                     # Sea-level density
    rho_1 = 0.36391 * (ureg.kg / ureg.m**3)                   # Density at 11,000 m (Tropopause)
    g = 9.80665 * (ureg.m / ureg.s**2)                        # Gravity
    R = 8.3144598 * ((ureg.N * ureg.m) / (ureg.mol * ureg.K)) # Universal gas constant
    M = 0.0289644 * (ureg.kg / ureg.mol)                      # Molar mass of dry air
    temperature_0 = 288.15 * ureg.K                           # Sea-level standard temperature
    lapse_rate = 0.0065 * (ureg.K / ureg.m)                   # Temperature lapse rate
    temperature_stratosphere = 216.65 * ureg.K                # Constant temperature in the lower Stratosphere

    if altitude <= 11000 * ureg.m:
        current_temp = _calculate_atmospheric_temperature(altitude).to(ureg.K)
        exponent = (g * M / (R * lapse_rate)) - 1
        rho = rho_0 * (current_temp / temperature_0) ** exponent
    else:
        # This part was already correct
        rho = rho_1 * math.exp(
            -g * M * (altitude - 11000 * ureg.m) / (R * temperature_stratosphere)
        )

    return rho.to(ureg.kg / ureg.m**3)


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


    See Also
    --------
    [Dynamic Pressure entry on Wikipedia](https://en.wikipedia.org/wiki/Dynamic_pressure)

    References
    --------
    Eqn. (2.63) in in Young, T. M. (2018). Performance of the Jet Transport Airplane. _John Wiley & Sons_. doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

    Parameters
    ----------
    speed : float
        Aircraft speed [speed]
    altitude : float
        Aircraft altitude above sea level [distance]

    Returns
    -------
    ureg.Quantity (float) [pressure]
        Dynamic pressure (Pascals).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.utility.physics import _calculate_dynamic_pressure
    _calculate_dynamic_pressure(
        speed=833*ureg.kph,
        altitude=10000*ureg.m
    )
    ```
    """
    air_density = _calculate_atmospheric_density(altitude)
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

    Returns
    -------
    ureg.Quantity (float) [speed]
        Aircraft velocity (km/h).

    See Also
    --------
    [Mach Number entry on Wikipedia](https://en.wikipedia.org/wiki/Mach_number#Calculation)

    References
    ----------
    Eqn.(1.33)-(1.34) Sadraey, M. H. (2017). Aircraft Performance: An Engineering Approach . _CRC Press_. doi:[10.1201/9781003279068](https://doi.org/10.1201/9781003279068)

    Returns
    -------
    ureg.Quantity (float) [speed]
        Aircraft velocity in kilometers per hour.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.utility.physics import _calculate_aircraft_velocity
    _calculate_aircraft_velocity(
        mach_number=0.8,
        altitude=10000*ureg.m
    )
    ```
    """
    temperature = _calculate_atmospheric_temperature(altitude)

    R = 287.052874 * (ureg.J/(ureg.kg*ureg.K)) # specific gas constant for air 
    gamma = 1.4 * ureg.dimensionless # ratio of specific heat for air
    velocity = mach_number * (gamma * R * temperature.to(ureg.K)) ** 0.5

    return velocity.to(ureg.kph)


@ureg.check('[temperature]')
def _calculate_speed_of_sound(temperature):
    r"""
    Computes the speed of sound in air as a function of temperature uses the relationship for an ideal gas:

    $$
    a = a_0 \sqrt{\frac{T}{T_0}}
    $$
    
    Or equivalently:
    
    $$
    a = \sqrt{\gamma R T}
    $$

    where:
    
    | Symbol   | Dimension                | Description                     | Value             |
    |----------|--------------------------|---------------------------------|-------------------|
    | $a$      | [velocity]               | speed of sound                  | N/A               |
    | $a_0$    | [velocity]               | speed of sound at sea level     | 340.29 m/s        |
    | $T$      | [temperature]            | local air temperature           | N/A               |
    | $T_0$    | [temperature]            | standard sea level temp         | 288.15 K          |
    | $\gamma$ | [dimensionless]          | ratio of specific heats         | 1.40              |
    | $R$      | [energy/(mass*temp)]     | gas constant                    | 287.05 m²/(s²K)   |

    See Also
    --------
    [`jetfuelburn.utility.physics._calculate_atmospheric_temperature`][]

    References
    ----------
    Eqn. (2.77) in Young, T. M. (2018). Performance of the Jet Transport Airplane. _John Wiley & Sons_. doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

    Parameters
    ----------
    temperature : Quantity [temperature]
        The local air temperature.

    Returns
    -------
    ureg.Quantity (float) [velocity]
        Speed of sound (km/h).

    Raises
    ------
    ValueError
        If temperature is below absolute zero.
    """
    T_val = temperature.to(ureg.kelvin)
    if T_val.magnitude < 0:
        raise ValueError("Temperature must be above absolute zero. If you really did manage to measure a temperature below absolute zero, please contact the JetFuelBurn developers.")
    
    a0 = 661.479 * ureg.knot   # Standard speed of sound at sea level
    T0 = 288.15 * ureg.kelvin  # Standard sea level temperature    
    
    speed_of_sound = a0 * math.sqrt((T_val / T0).magnitude)
    
    return speed_of_sound.to(ureg.kph)