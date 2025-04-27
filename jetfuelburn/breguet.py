from jetfuelburn import ureg
import math

@ureg.check(
    '[length]',
    '[]',
    '[mass]',
    '[speed]',
    '[time]/[length]' # [mg/Ns] = s/m
)
def calculate_fuel_consumption_range_equation(
    R: float,
    LD: float,
    m_after_cruise: float,
    v_cruise: float,
    TSFC_cruise: float,
) -> float:
    r"""
    Given a flight distance (=range) $R$ and aircraft performance parameters (see table),
    returns the fuel mass burned during the flight $m_f$ [kg] based on the Breguet range equation.

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
    Like any adaption of the range equation, this fuel calculation function represents a simplification of actual flight dynamics.
    Specifically, this function implements the Breguet range equation under the assumption of
    constant-airspeed and constant-lift-coefficient flight (cf. Young (2018), Sec. 13.7.2).

    References
    --------
    - Young, T. M. (2017).
    _Performance of the Jet Transport Airplane: Analysis Methods, Flight Operations, and Regulations._
    John Wiley & Sons.
    doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)
    - [Range (Aeronautics), Wikipedia](https://en.wikipedia.org/wiki/Range_(aeronautics))

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
    v_cruise : float
        Average cruise speed of the aircraft (TAS) [speed]
    TSFC_cruise : float
        Average Thrust Specific Fuel Consumption of the aircraft during cruise [time/distance (results from the definition of TSFC)]

    Returns
    -------
    float
        Required fuel mass [kg]

    Example
    -------
    ```pyodide install='jetfuelburn' assets='no'
    from jetfuelburn.breguet import calculate_fuel_consumption_range_equation
    calculate_fuel_consumption_range_equation(
        R=2000*ureg.nmi,
        LD=18,
        m_after_cruise=100*ureg.metric_ton,
        v_cruise=800*ureg.kph,
        TSFC_cruise=17*(ureg.mg/ureg.N/ureg.s),
    )
    ```
    """

    if R < 0:
        raise ValueError("Range must be greater than zero.")
    if LD <= 1:
        raise ValueError("Lift-to-Drag ratio must be greater than 1.")
    if m_after_cruise < 0:
        raise ValueError("Mass after cruise must be greater than zero.")
    if v_cruise <= 0:
        raise ValueError("Cruise speed must be greater than zero.")
    if TSFC_cruise <= 0:
        raise ValueError("Thrust Specific Fuel Consumption must be greater than zero.")

    if R==0:
        return 0 * ureg.kg
    else:
        g = 9.81 * (ureg.meter/ureg.second**2)
        m_fuel =  m_after_cruise * (math.exp((R * TSFC_cruise * g) / (LD * v_cruise)) - 1)
        return m_fuel.to('kg')