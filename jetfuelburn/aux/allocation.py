def footprint_allocation_by_area(
    fuel_per_flight: float,
    size_factor_eco: float,
    size_factor_premiumeco: float,
    size_factor_business: float,
    size_factor_first: float,
    seats_eco: int,
    seats_premiumeco: int,
    seats_business: int,
    seats_first: int,
    load_factor_eco: float,
    load_factor_premiumeco: float,
    load_factor_business: float,
    load_factor_first: float,
) -> dict[float, float, float, float]:
    r"""
    Given the fuel burn per flight $F$, the number of seats in each cabin class $S_i$,
    the load factor in each cabin class $L_i$ and the size factor of each cabin class $s_i$,
    returns the fuel burn per passenger specific to each cabin class $f_i$.

    $$
        f_i = \frac{1}{L_i} \frac{s_i F}{\sum_i s_i S_i}
    $$

    where

    | Symbol | Unit (eg.)    | Description                                  |
    | ------ | ------------- | -------------------------------------------- |
    | $F$    | kg            | Fuel burn per flight                         |
    | $f_i$  | kg            | Fuel burn per passenger in seating class $i$ |
    | $L_i$  | dimensionless | Load factor in seating class $i$             |
    | $s_i$  | dimensionless | Size factor of seating class $i$             |
    | $S_i$  | dimensionless | Number of seats in seating class $i$         |

    Summing over the fuel burn of all seating classes, we again get the total fuel burn per flight $F$:

    $$
    F = \sum_i f_i S_i L_i = \sum_i \frac{1}{L_i} \frac{s_i F}{\sum_i s_i S_i} S_i L_i = F \frac{\sum_i s_i}{\sum_i s_i}
    $$

    The _size factor_ of a class is defined as:
    
    $$
        s_i = \frac{A_i}{A_{economy}}
    $$

    where $A_i$ is the area occupied by a passenger in class $i$ and
    $A_{economy}$ is the area occupied by a passenger in economy class.

    This approach is suggested by both ICAO and IATA as the "allocation by area" method.

    Notes
    -----
    IATA RP 1726 (Section 2.4.2) recommends the following size factors:

    |             | Economy | Premium Economy | Business | First |
    | ----------- | ------- | --------------- | -------- | ----- |
    | __Narrow-Body__ | 1.0     | 1.00            | 1.5      | 1.5   |
    | __Wide-Body__   | 1.0     | 1.5             | 4.0      | 5.0   |

    Warnings
    --------
    If a certain seating class is not present, all related parameters
    (`seats`, `size_factor`, `load_factor`) should be set to 0.

    References
    --------
    - [IATA Recommended Practice RP 1726: Passenger CO2 Calculation Methodology](https://web.archive.org/web/20230526103741/https://www.iata.org/contentassets/139d686fa8f34c4ba7a41f7ba3e026e7/iata-rp-1726_passenger-co2.pdf)
    - [ICAO Carbon Emissions Calculator Methodology (Version 13.1)](https://web.archive.org/web/20240826103513/https://applications.icao.int/icec/Methodology%20ICAO%20Carbon%20Emissions%20Calculator_v13_Final.pdf)


    Raises
    ------
    ValueError
        If `fuel_per_flight` < 0 or
        (`load_factor_eco`, `load_factor_premiumeco`, `load_factor_business`, `load_factor_first`) not between 0 and 1.

    Parameters
    ----------
    fuel_per_flight : float
        Fuel burn per flight.
    size_factor_eco : float
        Size factor for economy class (1 by definition).
    size_factor_premiumeco : float
        Size factor for premium economy class.
    size_factor_business : float
        Size factor for business class.
    size_factor_first : float
        Size factor for first class.
    seats_eco : int
        Number of seats in economy class.
    seats_premiumeco : int
        Number of seats in premium economy class.
    seats_business : int
        Number of seats in business class.
    seats_first : int
        Number of seats in first class.
    load_factor_eco : float
        Load factor for economy class (between 0 and 1).
    load_factor_premiumeco : float
        Load factor for premium economy class (between 0 and 1).
    load_factor_business : float
        Load factor for business class (between 0 and 1).
    load_factor_first : float
        Load factor for first class (between 0 and 1).
        
    Returns
    -------
    dict[float, float, float, float]
        Fuel burn per passenger per flight in economy, premium economy, business and first class.

    Example
    -------
    ```pyodide install="jetfuelburn"
    from jetfuelburn import ureg
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
    )
    ```
    """

    if not fuel_per_flight > 0:
        raise ValueError("Fuel burn per flight must be >0.")
    if not (0 <= load_factor_eco <= 1):
        raise ValueError("Load factor (economy class) must be between 0 and 1.")
    if not (0 <= load_factor_premiumeco <= 1):
        raise ValueError("Load factor (premium economy class) must be between 0 and 1.")
    if not (0 <= load_factor_business <= 1):
        raise ValueError("Load factor (business class) must be between 0 and 1.")
    if not (0 <= load_factor_first <= 1):
        raise ValueError("Load factor (first class) must be between 0 and 1.")

    if size_factor_eco !=1 or seats_eco == 0:
        raise ValueError("Economy class must have size factor 1 and at least one seat.")
    fuel_eco = (1/load_factor_eco) * (size_factor_eco * fuel_per_flight) / (
        size_factor_eco * seats_eco +
        size_factor_premiumeco * seats_premiumeco +
        size_factor_business * seats_business +
        size_factor_first * seats_first
    )
    if load_factor_premiumeco == 0 or seats_premiumeco == 0:
        fuel_premiumeco = 0
    else:
        fuel_premiumeco = (1/load_factor_premiumeco) * (size_factor_premiumeco * fuel_per_flight) / (
            size_factor_eco * seats_eco +
            size_factor_premiumeco * seats_premiumeco +
            size_factor_business * seats_business +
            size_factor_first * seats_first
        )
    if load_factor_business == 0 or seats_business == 0:
        fuel_business = 0
    else:
        fuel_business = (1/load_factor_business) * (size_factor_business * fuel_per_flight) / (
            size_factor_eco * seats_eco +
            size_factor_premiumeco * seats_premiumeco +
            size_factor_business * seats_business +
            size_factor_first * seats_first
        )
    if load_factor_first == 0 or seats_first == 0:
        fuel_first = 0
    else:
        fuel_first = (1/load_factor_first) * (size_factor_first * fuel_per_flight) / (
            size_factor_eco * seats_eco +
            size_factor_premiumeco * seats_premiumeco +
            size_factor_business * seats_business +
            size_factor_first * seats_first
        )

    return {
        'fuel_eco': fuel_eco,
        'fuel_premiumeco': fuel_premiumeco,
        'fuel_business': fuel_business,
        'fuel_first': fuel_first
    }