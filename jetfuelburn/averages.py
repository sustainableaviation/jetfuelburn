from jetfuelburn import ureg
import math


class myclimate:
    r"""
    This class implements the public part of the myClimate Flight Emissions Calculator.

    Fuel burn is calculated using a quadratic function of the form
    defined in the myClimate Flight Emissions Calculator Calculation Principles:

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
    As of early 2025, the myClimate calculator offers a selection of 10 specific aircraft types.
    For 4 of these, specific parameters are provided on the Flight Emissions Calculator Calculation Principles page:

    | Size Category         | Range [km]    | # of Seats         |
    |-----------------------|---------------|--------------------|
    | "standard short-haul" | $<1500km$     | 157.86             |
    | "standard long-haul"  | $>2500km$     | 302.58             |
    | B737                  | not provided  | 148.00             |
    | A320                  | not provided  | 165.00             |
    | A330                  | not provided  | 287.00             |
    | B777                  | not provided  | 370.00             |

    Key assumptions of this fuel calculation function:

    | Parameter         | Assumption                                                                 |
    |-------------------|----------------------------------------------------------------------------|
    | data availability | N/A, fleet-average values only                                             |
    | aircraft payload  | average                                                                    |
    | climb/descent     | considered in "LTO" factor, which is not made public                       |
    | fuel reserves     | not considered explicitly                                                  |
    | alternate airport | not considered explicitly                                                  |

    References
    ----------
    [myClimate Flight Emissions Calculator Calculation Principles](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/)

    Examples
    --------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.averages import myclimate
    myclimate.available_aircraft()[0:10]
    myclimate.calculate_fuel_consumption(
        acft='B737',
        x=2200*ureg.km,
    )
    ```
    """

    _regression_coefficients = {
        'A320': {'a': 0.00016, 'b': 1.454, 'c': 1531.722},
        'B737': {'a': 0.000032, 'b': 2.588, 'c': 1212.084 },
        'A330': {'a': 0.00034, 'b': 4.384, 'c': 2457.737},
        'B777': {'a': 0.00034, 'b': 6.112, 'c': 3403.041},
        'standard aircraft': {},
    }

    @staticmethod
    def available_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(myclimate._regression_coefficients.keys())

    @staticmethod
    @ureg.check(
         None, # acft
        '[length]',
    )
    def calculate_fuel_consumption(
        acft: str,
        x: float,
    ) -> float:
        r"""
        Given a flight distance, calculate the fleet-average fuel consumption of a flight using the
        [myClimate Flight Emissions Calculator](https://co2.myclimate.org/en/flight_calculators/new).

        Warnings
        --------
        It is not entirely clear from the description of the myClimate Flight Emissions Calculator
        how distances of <1500km for short-haul aircraft and distances of >2500km for long-haul aircraft
        are handled. [The description](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/) mentions that

        > "The fuel consumption for distances between 1500 and 2500 km is linearly interpolated."

        but this would make sense only for the "standard short-haul" and "standard long-haul" aircraft?

        In this function, short-haul aircraft can therefore only be used for distances of <1500km
        and long-haul aircraft can only be used for distances of >2500km. The `standard aircraft` option
        can be used for all distances.

        Parameters
        ----------
        x : float
            Mission distance [length].

        Returns
        -------
        float
            Fuel consumption [mass] in kg.
        """
        if x < (0 * ureg.km):
            raise ValueError("Distance must not be negative.")
        x = x.to('km').magnitude

        if acft in ['A320', 'B737'] and x > 2500:
            raise ValueError(f"Aircraft {acft} is not valid for distances > 2500 km.")
        if acft in ['A330', 'B777'] and x < 1500:
            raise ValueError(f"Aircraft {acft} is not valid for distances < 1500 km.")
        
        if acft == 'standard aircraft':
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
        else:
            a = myclimate._regression_coefficients[acft]['a']
            b = myclimate._regression_coefficients[acft]['b']
            c = myclimate._regression_coefficients[acft]['c']

        return (a * x**2 + b * x + c) * ureg.kg