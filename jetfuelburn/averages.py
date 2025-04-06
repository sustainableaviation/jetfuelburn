from jetfuelburn import ureg
import math


@ureg.check('[length]')
def calculate_fuel_consumption_myclimate(
    x: float,
) -> float:
    r"""
    Calculate the fuel consumption for a given distance and aircraft size using the myClimate Flight Emissions Calculator.

    Parameters
    ----------
    x : float
        Mission distance [length].

    $$
    f(x) + LTO = ax^2 + bx + c
    $$

    where:

    | Symbol     | Dimension         | Description                                                            |
    |------------|-------------------|------------------------------------------------------------------------|
    | $f(x)$     | [mass]            | Fuel consumption (cruise) in kg                                        |
    | $LTO$      | [mass]            | Fuel consumption (landing-takeoff-cycle (LTO)) in kg                   |
    | $x$        | [distance]        | Distance in km                                                         |
    | $a$        | [mass]            | Coefficient of the quadratic term                                      |
    | $b$        | [mass]            | Coefficient of the linear term                                         |
    | $c$        | [mass]            | Coefficient of the constant term                                       |

    Notes
    -----
    Data is available for 8 aircraft size classes, as defined in the myClimate Flight Emissions Calculator Calculation Principles:

    | Size Category         | Range [km]    | # of Seats         |
    |-----------------------|---------------|--------------------|
    | Standard short-haul   | $<1500km$     | 157.86             |
    | Standard long-haul    | $>2500km$     | 302.58             |

    References
    ----------
    [myClimate Flight Emissions Calculator Calculation Principles](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/)
    """
    if x < 0.ureg.km:
        raise ValueError("Distance must not be negative.")
    x = x.to('km').magnitude
    
    if x < 1500:
        a = 0.000007
        b = 2.775
        c = 1260.608
    elif x < 2500:
        a = 0.000007 + 0.000283 * (x - 1500) / 1000
        b = 2.775 + 0.7 * (x - 1500) / 1000
        c = 1260.608 + 1999.083 * (x - 1500) / 1000
    elif x >= 2500:
        a = 0.00029
        b = 3.475
        c = 3259.691

    return (a * x**2 + b * x + c) * ureg.('kg')



