# %%
import pint
from jetfuelburn import ureg
import math
from typing import Callable

from jetfuelburn.utility.physics import _calculate_atmospheric_density
from jetfuelburn.utility.code import _validate_function



class IntegratedRangeCalculator:
    """
    Performs numerical integration of the Specific Air Range (SAR) to estimate 
    cruise performance. Supports both static and dynamic TSFC models.
    """
    def __init__(
        self, 
        func_or_scalar_tsfc: pint.Quantity[int | float] | Callable,
        func_or_scalar_lift_to_drag: int | float | pint.Quantity[int | float] | Callable, 
    ):
        r"""
        """
        if isinstance(func_or_scalar_tsfc, pint.Quantity):
            self.func_tsfc = lambda M, H, F: func_or_scalar_tsfc
        elif callable(func_or_scalar_tsfc):
            # If dynamic, validate it and use it directly
            self._validate_function(
                func=func_or_scalar_tsfc,
                required_params={'M', 'H', 'F'},
                expected_return_type=pint.Quantity
            )
            self.func_tsfc = func_or_scalar_tsfc
        else:
            raise TypeError("tsfc must be a pint.Quantity or a callable.")

        if isinstance(func_or_scalar_lift_to_drag, (int, float, pint.Quantity)):
            self.func_drag = lambda L, M, h: L / func_or_scalar_lift_to_drag
        elif callable(func_or_scalar_lift_to_drag):
            self._validate_function(
                func=func_or_scalar_lift_to_drag,
                required_params={'L', 'M', 'h'},
                expected_return_type=pint.Quantity
            )
            self.func_drag = func_or_scalar_lift_to_drag
        else:
            raise TypeError("lift_to_drag must be a scalar or a callable.")
        
    
    @ureg.check(
        None,
        '[mass]',
        '[mass]',
        '[length]',
        '[speed]',
        None
    )
    def compute_integrated_range(
        self,
        m_start: pint.Quantity[int | float],
        m_end: pint.Quantity[int | float],
        h: pint.Quantity[int | float],
        V: pint.Quantity[int | float],
        num_intervals: int = 20,
    ):
        r"""
        asdf

        """
        m_start = m_start.to("kg")
        m_end = m_end.to("kg")
        m_increment = (m_end - m_start) / (num_intervals - 1)
        m_stations = [(m_start + i * m_increment) for i in range(num_intervals)]

        # 2. Performance Parameters
        ranges = [Q_(0, "nautical_mile")]
        times = [Q_(0, "hour")]
        list_SAR_at_station = []
        list_fuel_burn_per_distance = [] # New list for Fuel Burn per Distance
        #TODO: convert speed to mach number based on altitude

        # 3. Loop
        for m_station in m_stations:
            L = m_station * ureg.gravity
            D = self.func_drag(
                L=L,
                M=,
                h=h
            )
            TSFC = self.func_tsfc(
                M=M,
                h=h,
                F=D
            )
            fuel_flow = D * TSFC
            
            
            SAR = (V / fuel_flow).to("km / kg")
            list_SAR_at_station.append(SAR)

            fb_dist = (1 / SAR).to("kg / km")
            list_fuel_burn_per_distance.append(fb_dist)

        # 4. Integrate Range (Standard Procedure)
        cumulative_r = 0 * ureg.km
        cumulative_t = 0 * ureg.hour
        
        for i in range(len(m_stations) - 1):
            SAR_avg = (list_SAR_at_station[i] + list_SAR_at_station[i+1]) / 2
            dw_force = m_stations[i] - m_stations[i+1]
            dw_mass = (dw_force / ureg.standard_gravity).to("kg")
            
            dr = SAR_avg * dw_mass
            dt = dr / V
            
            cumulative_r += dr
            cumulative_t += dt
            ranges.append(cumulative_r)
            times.append(cumulative_t)
            
        return {
            "weight": weight_stations,
            "range": ranges,
            "time": times,
            "sar": sar_values,
            "fuel_burn_per_distance": fuel_burn_values # Return the new metric
        }


@ureg.check(
    '[length]',
    '[length]',
    '[]',
    '[]',
    '[mass]',
    '[area]',
    '[speed]',
    '[time]/[length]', # [mg/Ns] = s/m
)
def calculate_fuel_consumption_arctan(
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

    $$
        m_f = \frac{(B + m_{LDG}^2) \tan(\theta)}{\sqrt{B} - m_{LDG} \tan(\theta)}
    $$

    with

    \begin{align*}
    \theta &= \frac{R g TSFC}{2 E_{max} V} \\
    B &= \left( \frac{C_{D_0}}{K} \right) \left( \frac{\rho V^2 S}{2g} \right)^2
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

    References
    ----------
    Eqn. 13.25a ff. in 
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
    if R==0 * ureg.meter:
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
    B = (C_D0 / K) * ((rho * V**2 * S) / (2 * ureg.gravity))**2
    m_fuel = ((B + m_after_cruise**2) * math.tan(theta)) / (B**0.5 - m_after_cruise * math.tan(theta)) # math.sqrt(pint.Quantity) is not supported
    return m_fuel.to('kg')


@ureg.check(
    '[length]',
    '[]',
    '[mass]',
    '[speed]',
    '[speed]',
    '[time]/[length]', # [mg/Ns] = s/m
    '[]',
    '[]',
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
    returns the fuel mass burned during the flight $m_f$ [kg] based on the improved Breguet range equation from Randle et al. (2011).

    This improved Breguet range equation accounts for headwind effects
    as well as lost fuel during takeoff and climb and recovered fuel during descent and landing.

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
    instead of weight [N] for the fuel mass.

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
    if R==0 * ureg.meter:
        return 0 * ureg.kg
    else:
        H = (LD * V) / (TSFC * ureg.gravity)
        m_fuel = m_after_cruise * (
            (1 / math.exp( (-R / H) * (1 - (V_headwind / V)) )) 
            - lost_fuel_fraction 
            + recovered_fuel_fraction
            - 1
        )
        return m_fuel.to('kg')


@ureg.check(
    '[length]',
    '[]',
    '[mass]',
    '[speed]',
    '[time]/[length]' # [mg/Ns] = s/m
)
def calculate_fuel_consumption_breguet(
    R: pint.Quantity[float | int],
    LD: float | int | pint.Quantity[float | int],
    m_after_cruise: pint.Quantity[float | int],
    V: pint.Quantity[float | int],
    TSFC: pint.Quantity[float | int],
) -> float:
    r"""
    Given a flight distance (=range) $R$ and basic aircraft performance parameters (see table),
    returns the fuel mass burned during the flight $m_f$ [kg] based on the Breguet range equation.

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

    if R==0 * ureg.meter:
        return 0 * ureg.kg
    else:
        m_fuel =  m_after_cruise * (math.exp((R * TSFC * ureg.gravity) / (LD * V)) - 1)
        return m_fuel.to('kg')