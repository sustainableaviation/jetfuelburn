# %%
import pint
from jetfuelburn import ureg
import math
from typing import Callable

from jetfuelburn.utility.physics import (
    _calculate_atmospheric_density,
    _calculate_airspeed_from_mach,
)
from jetfuelburn.utility.code import (
    _validate_physics_function_parameters,
    _normalize_physics_function_or_scalar,
)


@ureg.check(
    "[mass]",
    "[length]",
    "[length]",
    "[]",
    None,
    None,
    "[mass]",
)
def calculate_fuel_consumption_stepclimb_integration(
    m_after_cruise: pint.Quantity,
    R: pint.Quantity,
    h: pint.Quantity,
    M: float,
    TSFC: pint.Quantity | Callable,
    LD: float | pint.Quantity | Callable,
    integration_mass_step: pint.Quantity = 100 * ureg.kg,
) -> pint.Quantity:
    r"""
    Given a flight distance (=range) $R$ and basic aircraft performance parameters (see table),
    returns the fuel mass burned during the flight $m_f$ [kg] based on a flight schedule 
    where aircraft velocity and altitude are constant during cruise, while allowing for variable thrust-specific fuel consumption
    and lift-to-drag ratio as a function of Mach number and altitude.

    Fuel mass is calculated through numerical integration of the specific air range (SAR) over the flight distance, using the trapezoidal rule:

    \begin{align*}
        R &\approx \sum_{i=0}^{n-1} \frac{r_a(m_i) + r_a(m_{i+1})}{2} \cdot (m_{i+1} - m_i) \\
        r_a &= \frac{M \cdot a_0 \sqrt{\Theta} \cdot (L/D)}{\text{TSFC} \cdot L}
    \end{align*}

    where:

    | Symbol     | Dimension         | Description                                                                                                              |
    |------------|-------------------|--------------------------------------------------------------------------------------------------------------------------|
    | $m_{fuel}$ | [mass]            | Fuel required for the mission of the aircraft                                                                            |
    | $R$        | [distance]        | Range of the aircraft (=mission distance)                                                                                |
    | $h$        | [length]          | Cruise altitude of the aircraft                                                                                          |
    | $M$        | [dimensionless]   | Mach number during cruise                                                                                                |
    | $TSFC$     | [time/distance]   | Thrust Specific Fuel Consumption of the aircraft during cruise                                                           |
    | $L/D$      | [dimensionless]   | Lift-to-drag ratio of the aircraft during cruise                                                                         |
    | $a_0$      | [speed]           | Speed of sound at sea level                                                                                              |
    | $\Theta$   | [dimensionless]   | Temperature ratio at cruise altitude (temperature at cruise altitude divided by temperature at sea level)               |
    | $m_i$      | [mass]            | Mass of the aircraft at step $i$ during cruise, starting with $m_0 = m_{TO}$ and ending with $m_n = m_{LDG}$ (= $m_{after\_cruise}$) |
    | $g$        | [acceleration]    | Gravitational acceleration                                                                                               |


    ??? info "Derivation"

        Equation 19 in Randle et al. (2011) expresses the fuel mass burned $m_f$
        during a flight of distance $s$ (=range $R$) as a function of the takeoff mass $m_{TO}$.
        However, in practical applications, the more relevant known parameter is the landing mass after cruise 
        
        \begin{align}
        r_a &= -\frac{\text{d}x}{\text{d}m} \\
        \text{d}x &= -r_a \text{d}m \\
        R = \int_{start}^{end} \text{d}x &= -\int_{m_{TO}}^{m_{LDG}} r_a \text{d}m \\
        \end{align}

        with the specific air range (SAR) defined as:
        
        \begin{align}
        r_a &= -\frac{\text{d}x}{\text{d}m} \\
        r_a &= -\frac{\text{d}x/\text{d}t}{\text{d}m/\text{d}t} \\
        r_a &= \frac{V}{Q} \\
        \end{align}

        with the definition of true airspeed (=velocity) $V$ and fuel flow rate $Q$:
        
        \begin{align}
        V &= M \cdot a_0 \sqrt{\Theta} \\
        Q &= \text{TSFC} \cdot D  = \text{TSFC} \cdot \frac{L}{(L/D)}
        \end{align}

        \begin{align}
        R = \int_{m_{TO}}^{m_{LDG}} \frac{V}{Q} \text{d}m &= \int_{m_{TO}}^{m_{LDG}} \frac{M \cdot a_0 \sqrt{\Theta}}{\text{TSFC} \cdot \frac{L}{(L/D)}} \text{d}m \\
        R = \int_{m_{TO}}^{m_{LDG}} \frac{M \cdot a_0 \sqrt{\Theta} \cdot (L/D)}{\text{TSFC} \cdot L} \text{d}m &= \int_{m_{TO}}^{m_{LDG}} \frac{M \cdot a_0 \sqrt{\Theta} \cdot (L/D)}{\text{TSFC} \cdot m \cdot g} \text{d}m
        \end{align}

        which can now be solved through numerical integration, using the trapezoidal rule:

        \begin{equation}
        R \approx \sum_{i=0}^{n-1} \frac{r_a(m_i) + r_a(m_{i+1})}{2} \cdot (m_{i+1} - m_i)
        \end{equation}

    See Also
    --------
    [`jetfuelburn.rangeequation.calculate_fuel_consumption_stepclimb_arctan`][]

    References
    ----------
    Eqn. 13.1aff. and Eqn. 13.28a ff. in 
    Young, T. M. (2018). 
    Performance of the Jet Transport Airplane. 
    _John Wiley & Sons_. 
    doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

    Parameters
    ----------
    m_after_cruise : float
        Mass of the aircraft after cruise segment (eg. OEW + Payload + Crew + Reserves) [mass]
    R : float
        Range of the aircraft (=mission distance) [distance]
    h : float
        Cruise altitude of the aircraft [length]
    M : float
        Mach number during cruise [dimensionless]
    TSFC : float or Callable
        Thrust Specific Fuel Consumption of the aircraft during cruise, either as a constant value [time/distance] or as a function of Mach number and altitude.  
    LD : float or Callable
        Lift-to-drag ratio of the aircraft during cruise, either as a constant value [dimensionless] or as a function of lift, Mach number and altitude.  
    integration_mass_step : float
        Mass step for numerical integration [mass]. A smaller step will yield a more accurate result, but will also increase computation time. Default is 100 kg.
    
    Returns
    -------
    pint.Quantity [mass]
        Required fuel mass [kg]

    Raises
    ------
    ValueError
        If the dimensions of the inputs are invalid.
    ValueError
        If the magnitude of the inputs are invalid (eg. negative).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.rangeequation import calculate_integrated_range
    calculate_integrated_range(
        m_after_cruise=100*ureg.metric_ton,
        R=2000*ureg.nmi,
        h=35000*ureg.feet,
        M=0.78,
        TSFC=17*(ureg.mg/ureg.N/ureg.s),
        LD=18,
    )
    ```
    """
    if integration_mass_step < 1 * ureg.kg:
        raise ValueError("integration_mass_step must be at least 1 kg")
    if m_after_cruise <= 0 * ureg.kg:
        raise ValueError("m_after_cruise must be greater than zero")
    if M <= 0:
        raise ValueError("Mach number must be greater than zero")
    if h < 0 * ureg.meter:
        raise ValueError("Altitude must be non-negative")

    if type(TSFC) == Callable:
        _validate_physics_function_parameters(
            func=TSFC,
            required_params={"M", "h"},
        )
    if type(LD) == Callable:
        _validate_physics_function_parameters(
            func=LD,
            required_params={"L", "M", "h"},
        )
    func_TSFC: Callable = _normalize_physics_function_or_scalar(TSFC)
    func_LD: Callable = _normalize_physics_function_or_scalar(LD)

    m_after_cruise = m_after_cruise.to("kg")
    V = _calculate_airspeed_from_mach(mach_number=M, altitude=h)

    m_current = m_after_cruise
    R_current = 0 * ureg.km

    while R_current < R:
        L_A = m_current * ureg.gravity
        L_B = (m_current + integration_mass_step) * ureg.gravity
        SAR_A = (V * func_LD(L=L_A, M=M, h=h)) / (func_TSFC(M=M, h=h) * L_A)
        SAR_B = (V * func_LD(L=L_B, M=M, h=h)) / (func_TSFC(M=M, h=h) * L_B)
        SAR_avg = (SAR_A + SAR_B) / 2
        delta_R = (SAR_avg * integration_mass_step).to("km")
        R_current += delta_R
        m_current += integration_mass_step

        if R_current >= R:
            R_excess = R_current - R
            m_excess = R_excess / SAR_avg
            m_current -= m_excess
            break

    m_fuel = m_current - m_after_cruise
    return m_fuel.to("kg")


@ureg.check(
    "[length]",
    "[length]",
    "[]",
    "[]",
    "[mass]",
    "[area]",
    "[speed]",
    "[time]/[length]",  # [mg/Ns] = s/m
)
def calculate_fuel_consumption_stepclimb_arctan(
    R: pint.Quantity[float | int],
    h: pint.Quantity[float | int],
    K: float | int | pint.Quantity[float | int],
    C_D0: float | int | pint.Quantity[float | int],
    m_after_cruise: pint.Quantity[float | int],
    S: pint.Quantity[float | int],
    V: pint.Quantity[float | int],
    TSFC: pint.Quantity[float | int],
) -> float:
    r"""
    Given a flight distance (=range) $R$ and basic aircraft performance parameters (see table),
    returns the fuel mass burned during the flight $m_f$ [kg] based on a flight schedule where 
    aircraft velocity and altitude are constant during cruise.

    Fuel mass is calculated as:

    $$
        m_f = \frac{(B + m_{LDG}^2) \tan(\theta)}{\sqrt{B} - m_{LDG} \tan(\theta)}
    $$

    with

    \begin{align*}
        \theta &= \frac{R \cdot g \cdot TSFC}{2 E_{max} V} \\
        B &= \left( \frac{C_{D_0}}{K} \right) \left( \frac{\rho V^2 S}{2g} \right)^2 \\
        E_{max} &= \frac{1}{2 \sqrt{C_{D_0} K}}
    \end{align*}

    where:

    | Symbol     | Dimension         | Description                                                            |
    |------------|-------------------|------------------------------------------------------------------------|
    | $m_{fuel}$ | [mass]            | Fuel required for the mission of the aircraft                          |
    | $R$        | [distance]        | Range of the aircraft (=mission distance)                              |
    | $TSFC$     | [time/distance]   | Thrust Specific Fuel Consumption of the aircraft during cruise         |
    | $g$        | [acceleration]    | Acceleration due to gravity                                            |
    | $V$        | [speed]           | Average cruise speed of the aircraft (TAS)                             |
    | $E_{max}$  | [energy/mass]     | Maximum lift-to-drag ratio according to drag parabola                  |
    | $C_{D_0}$  | [dimensionless]   | Zero-lift drag coefficient of the aircraft                             |
    | $K$        | [dimensionless]   | Lift-dependent drag factor of the aircraft                             |
    | $\rho$     | [mass/volume]     | Air density at cruise altitude                                         |
    | $S$        | [area]            | Wing reference area of the aircraft                                    |


    ??? info "Derivation"

        Eqn. 7.43 in Young (2018) expresses the range $R$ of an aircraft as a function of the takeoff mass $m_1$ 
        and landing mass $m_2$ after cruise, as well as the aircraft performance parameters. 
        However, in practical applications, the fuel mass $m_f$ should be calculated based on the landing mass after cruise $m_2$.

        Starting from the definition of aircraft masses:

        \begin{align*}
        m_f &= m_1 - m_2 \\
        m_1 &= m_f + m_2 \\
        \end{align*}

        The expression for range can be rearranged:

        \begin{align*}
        R &= \frac{2E_{max}V}{g\bar{c}} \arctan\left\{ \frac{\sqrt{B_3}(m_1 - m_2)}{B_3 + m_1 m_2} \right\} \\
        \Theta &:= \frac{R g \bar{c}}{2 E_{max} V} \\
        \tan(\Theta) &= \frac{\sqrt{B_3}(m_1 - m_2)}{B_3 + m_1 m_2} \\
        \tan(\Theta) &= \frac{\sqrt{B_3} m_f}{B_3 + (m_f + m_2)m_2} \\
        \tan(\Theta)(B_3 + m_f m_2 + m_2^2) &= \sqrt{B_3} m_f \\
        B_3 \tan(\Theta) + m_f m_2 \tan(\Theta) + m_2^2 \tan(\Theta) &= \sqrt{B_3} m_f \\
        \tan(\Theta)(B_3 + m_2^2) &= m_f (\sqrt{B_3} - m_2 \tan(\Theta)) \\
        m_f &= \frac{(B_3 + m_2^2) \tan(\Theta)}{\sqrt{B_3} - m_2 \tan(\Theta)} \\
        \end{align*}

        where:

        \begin{equation*}
        B_3 = \left(\frac{C_{D_0}}{K}\right) \left(\frac{\rho V^2 S}{2g}\right)^2
        \end{equation*}
        

    References
    ----------
    Eqn. 7.43 and Eqn. 13.25a ff. in 
    Young, T. M. (2018). 
    Performance of the Jet Transport Airplane. 
    _John Wiley & Sons_. 
    doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.rangeequation import calculate_fuel_consumption_arctan
    calculate_fuel_consumption_arctan(
        R=2000*ureg.nmi,
        h=35000*ureg.feet,
        K=0.045,
        C_D0=0.02,
        m_after_cruise=100*ureg.metric_ton,
        S=122.6*ureg.meter**2,
        V=800*ureg.kph,
        TSFC=17*(ureg.mg/ureg.N/ureg.s),
    )
    ```

    """
    if R == 0 * ureg.meter:
        return 0 * ureg.kg
    if R < 0 * ureg.meter:
        raise ValueError("Range must be greater than zero.")
    if h < 0 * ureg.meter:
        raise ValueError("Altitude must be greater than zero.")
    if m_after_cruise < 0 * ureg.kg:
        raise ValueError("Mass after cruise must be greater than zero.")
    if S <= 1 * ureg.meter**2:
        raise ValueError("Lift-to-Drag ratio must be greater than 1.")
    if V <= 0 * ureg.kph:
        raise ValueError("Cruise speed must be greater than zero.")
    if TSFC.magnitude <= 0:
        raise ValueError("Thrust Specific Fuel Consumption must be greater than zero.")

    E_max = 0.5 * (1 / math.sqrt(C_D0 * K))
    rho = _calculate_atmospheric_density(altitude=h)
    theta = (R * ureg.gravity * TSFC) / (2 * E_max * V)
    B = (C_D0 / K) * ((rho * V**2 * S) / (2 * ureg.gravity)) ** 2
    m_fuel = ((B + m_after_cruise**2) * math.tan(theta)) / (
        B**0.5 - m_after_cruise * math.tan(theta)
    )  # math.sqrt(pint.Quantity) is not supported
    return m_fuel.to("kg")


@ureg.check(
    "[length]",
    "[]",
    "[mass]",
    "[speed]",
    "[speed]",
    "[time]/[length]",  # [mg/Ns] = s/m
    "[]",
    "[]",
)
def calculate_fuel_consumption_breguet_improved(
    R: pint.Quantity[float | int],
    LD: float | int | pint.Quantity[float | int],
    m_after_cruise: pint.Quantity[float | int],
    V: pint.Quantity[float | int],
    V_headwind: pint.Quantity[float | int],
    TSFC: pint.Quantity[float | int],
    lost_fuel_fraction: float | int | pint.Quantity[float | int] = 0.0152,
    recovered_fuel_fraction: float | int | pint.Quantity[float | int] = 0.001,
) -> float:
    r"""
    Given a flight distance (=range) $R$ and basic aircraft performance parameters (see table),
    returns the fuel mass burned during the flight $m_f$ [kg] based on a flight schedule 
    where the lift-coefficient and velocity are constant during cruise ("cruise-climb"), 
    while taking into account headwind effects and fuel losses during takeoff and climb, as well as fuel recovery during descent and landing. 

    Fuel mass is calculated as:

    $$
    m_{\text{fuel}} = m_{\text{LDG}} \left( \frac{1}{\exp\left\{ \frac{-R}{H \left(1 - \frac{V_{\text{HW}}}{V}\right)} \right\} - \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} + \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}}} - 1 \right)
    $$

    with

    $$
    H = \frac{L/D \cdot V}{TSFC \cdot g}
    $$

    where:

    | Symbol                      | Dimension         | Description                                                    |
    |-----------------------------|-------------------|----------------------------------------------------------------|
    | $m_{f}$                     | [mass]            | Fuel required for the mission of the aircraft                  |
    | $m_{LDG}$                   | [mass]            | Mass of the aircraft after cruise segment                      |
    | $R$                         | [distance]        | Range of the aircraft (=mission distance)                      |
    | $TSFC$                      | [time/distance]   | Thrust Specific Fuel Consumption of the aircraft during cruise |
    | $g$                         | [acceleration]    | Acceleration due to gravity                                    |
    | $L/D$                       | [dimensionless]   | Lift-to-Drag ratio of the aircraft                             |
    | $V$                         | [speed]           | Average speed of the aircraft (TAS)                            |
    | $V_{HW}$                    | [speed]           | Average speed of headwind component                            |
    | $\frac{\Delta m_L}{m_{TO}}$ | [dimensionless]   | Lost fuel fraction                                             |
    | $\frac{\Delta m_R}{m_{TO}}$ | [dimensionless]   | Recovered fuel fraction                                        | 

    ??? info "Derivation"

        Equation 19 in Randle et al. (2011) expresses the fuel mass burned $m_f$
        during a flight of distance $s$ (=range $R$) as a function of the takeoff mass $m_{TO}$.
        However, in practical applications, the more relevant known parameter is the landing mass after cruise 
        
        $m_{LDG}$ (= $m_{after\_cruise}$)
        
        Therefore, the equation is rearranged here to solve for $m_f$ as a function of $m_{LDG}$:

        \begin{align}
            m_f &= m_{\text{TO}} \left( 1 - e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}} \right) \\
            m_f &= (m_f + m_{\text{LDG}}) \left( 1 - e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}} \right) \\
            m_f &= (m_f + m_{\text{LDG}}) \cdot 1 + (m_f + m_{\text{LDG}}) \left( -e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}} \right) \\
            m_f &= m_f + m_{\text{LDG}} + (m_f + m_{\text{LDG}}) \left( -e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}} \right) \\
            0 &= m_{\text{LDG}} + (m_f + m_{\text{LDG}}) \left( -e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}} \right) \\
            -m_{\text{LDG}} &= (m_f + m_{\text{LDG}}) \left( -e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}} \right) \\
            \frac{-m_{\text{LDG}}}{-e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}}} &= m_f + m_{\text{LDG}} \\
            m_f &= \frac{-m_{\text{LDG}}}{-e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}}} - m_{\text{LDG}} \\
            m_f &= m_{\text{LDG}} \left( \frac{-1}{-e^{-\frac{s}{H}} + \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} - \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}}} - 1 \right) \\
            m_f &= m_{\text{LDG}} \left( \frac{1}{e^{-\frac{s}{H}} - \frac{\Delta m_{\text{lost}}}{m_{\text{TO}}} + \frac{\Delta m_{\text{rec}}}{m_{\text{TO}}}} - 1 \right)
        \end{align}

    Warnings
    --------
    Unlike the equation in Randle et al. (2011), this function uses mass [kg] 
    instead of weight [N] for the fuel.

    Notes
    -----
    Assumes a lost fuel fraction $\Delta m_{lost}=0.0152$ 
    and a recovered fuel fraction $\Delta m_{rec}=0.001$ as per 
    section D of Randle et al. (2011). 
    Values can be adjusted through function parameters.

    References
    --------
    Eqn. 19 in Randle, W. E., Hall, C. A., & Vera-Morales, M. (2011). 
    Improved range equation based on aircraft flight data. 
    _Journal of Aircraft_. 
    doi:[10.2514/1.C031262](https://doi.org/10.2514/1.C031262)

    See Also
    --------
    [`jetfuelburn.rangeequation.calculate_fuel_consumption_breguet`][]

    Raises
    ------
    ValueError
        If the dimensions of the inputs are invalid.
    ValueError
        If the magnitude of the inputs are invalid (eg. negative).
    
    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.rangeequation import calculate_fuel_consumption_breguet_improved
    calculate_fuel_consumption_breguet_improved(
        R=2000*ureg.nmi,
        LD=18,
        m_after_cruise=100*ureg.metric_ton,
        V=800*ureg.kph,
        V_headwind=50*ureg.kph,
        TSFC=17*(ureg.mg/ureg.N/ureg.s),
    )
    ```
    """
    if R == 0 * ureg.meter:
        return 0 * ureg.kg
    else:
        H = (LD * V) / (TSFC * ureg.gravity)
        m_fuel = m_after_cruise * (
            (1 / math.exp((-R / H) * (1 - (V_headwind / V))))
            - lost_fuel_fraction
            + recovered_fuel_fraction
            - 1
        )
        return m_fuel.to("kg")


@ureg.check("[length]", "[]", "[mass]", "[speed]", "[time]/[length]")  # [mg/Ns] = s/m
def calculate_fuel_consumption_breguet(
    R: pint.Quantity[float | int],
    LD: float | int | pint.Quantity[float | int],
    m_after_cruise: pint.Quantity[float | int],
    V: pint.Quantity[float | int],
    TSFC: pint.Quantity[float | int],
) -> float:
    r"""
    Given a flight distance (=range) $R$ and basic aircraft performance parameters (see table),
    returns the fuel mass burned during the flight $m_f$ [kg] based on a flight schedule where
    the lift-coefficient and velocity are constant during cruise ("cruise-climb").
    This solution is also known as the **Breguet range equation**.

    Fuel mass is calculated as:

    $$
        m_f = (e^{\frac{R \cdot TSFC \cdot g}{L/D \cdot v}} - 1 ) m_2
    $$

    where:

    | Symbol     | Dimension         | Description                                                            |
    |------------|-------------------|------------------------------------------------------------------------|
    | $m_{fuel}$ | [mass]            | Fuel required for the mission of the aircraft                          |
    | $R$        | [distance]        | Range of the aircraft (=mission distance)                              |
    | $TSFC$     | [time/distance]   | Thrust Specific Fuel Consumption of the aircraft during cruise         |
    | $g$        | [acceleration]    | Acceleration due to gravity                                            |
    | $L/D$      | [dimensionless]   | Lift-to-Drag ratio of the aircraft                                     |
    | $v$        | [speed]           | Average cruise speed of the aircraft (TAS)                             |
    | $m_2$      | [mass]            | Mass of the aircraft after cruise segment                              |

    Note that thrust-specific fuel consumption (TSFC) is of dimension [time/distance], as the commonly used unit [g/kNs] simplifies accordingly.

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter         | Assumption                                                                 |
    |-------------------|----------------------------------------------------------------------------|
    | data availability | adequate for both current aircraft (reports) and future aircraft (studies) |
    | aircraft payload  | variable                                                                   |
    | climb/descent     | not considered, only cruise-phase                                          |
    | fuel reserves     | can be considered through $m_2$                                            |
    | alternate airport | can be considered through $m_2$                                            |

    Warnings
    --------
    This analytical fuel calculation method represents a simplification of actual flight dynamics.
    Specifically, this function assumes a _flight schedule_ with constant airspeed and constant lift coefficient, resulting in a cruise-climb.
    Young (2017) shows this in Section 13.3.3 "Second Flight Schedule":

    > (...) the airplane must be flown in a way that will ensure that the ratio (...) [of weight to air density] remains constant.
    > This is possible if the airplane is allowed to climb very slowly so that the relative density (...) decreases in direct proportion to the decrease in airplane weight (...).

    References
    --------
    - Young, T. M. (2018).
    Performance of the Jet Transport Airplane (Section 13.7.3 "Fuel Required for Specified Range"). _John Wiley & Sons_. doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)
    - Cavcar, M. (2006). Bréguet range equation?. _Journal of Aircraft_. doi:[10.2514/1.17696](https://doi.org/10.2514/1.17696)
    - [Range (Aeronautics) entry on Wikipedia](https://en.wikipedia.org/wiki/Range_(aeronautics))

    See Also
    --------
    [`jetfuelburn.rangeequation.calculate_fuel_consumption_breguet_improved`][]

    Raises
    ------
    ValueError
        If the dimensions of the inputs are invalid.
    ValueError
        If the magnitude of the inputs are invalid (eg. negative).

    Parameters
    ----------
    R : float
        Range of the aircraft (=mission distance) [distance]
    LD : float
        Lift-to-Drag ratio of the aircraft [dimensionless]
    m_after_cruise : float
        Mass of the aircraft after landing (eg. OEW + Payload + Crew + Reserves) [mass]
    V : float
        Average cruise speed of the aircraft (TAS) [speed]
    TSFC : float
        Average Thrust Specific Fuel Consumption of the aircraft during cruise [time/distance (results from the definition of TSFC)]

    Returns
    -------
    float
        Required fuel mass [kg]

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.rangeequation import calculate_fuel_consumption_breguet
    calculate_fuel_consumption_breguet(
        R=2000*ureg.nmi,
        LD=18,
        m_after_cruise=100*ureg.metric_ton,
        V=800*ureg.kph,
        TSFC=17*(ureg.mg/ureg.N/ureg.s),
    )
    ```
    """

    if R.magnitude < 0:
        raise ValueError("Range must be greater than zero.")
    if LD <= 1:
        raise ValueError("Lift-to-Drag ratio must be greater than 1.")
    if m_after_cruise < 0 * ureg.kg:
        raise ValueError("Mass after cruise must be greater than zero.")
    if V <= 0 * ureg.kph:
        raise ValueError("Cruise speed must be greater than zero.")
    if TSFC.magnitude <= 0:
        raise ValueError("Thrust Specific Fuel Consumption must be greater than zero.")

    if R == 0 * ureg.meter:
        return 0 * ureg.kg
    else:
        m_fuel = m_after_cruise * (math.exp((R * TSFC * ureg.gravity) / (LD * V)) - 1)
        return m_fuel.to("kg")
