# %%

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


def calculate_fuel_consumption_based_on_payload_range(
    d: float,
    oew: float,
    mtow: float,
    payload_point_A: float,
    range_point_A: float,
    payload_point_B: float,
    range_point_B: float,
    range_point_C: float,
) -> tuple[ureg.Quantity, ureg.Quantity]:
    """
    Given aircraft performance parameters from a payload/range diagram and a flight distance,
    calculates the fuel burned and payload mass for a given mission.

    Parameters
    ----------
    d : float
        Flight distance [length]
    oew : float
        Operating Empty Weight (OEW) of the aircraft [mass]
    mtow : float
        Maximum Takeoff Weight (MTOW) of the aircraft [mass]
    payload_point_A : float
        Payload mass at point A [mass]
    range_point_A : float
        Range at point A [length]
    payload_point_B : float
        Payload mass at point B [mass]
    range_point_B : float
        Range at point B [length]
    range_point_C : float
        Range at point C [length]

    Warnings
    --------
    There is no manufacturer-independent convention for including
    reserve and alternate fuel in payload/range diagrams.
    Limited evidence suggests that eg. Boeing always assumes a 200nmi diversion distance.
    The user is therefore cautioned against directly comparing aircraft of different manufacturers.

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter         | Assumption                                                          |
    |-------------------|---------------------------------------------------------------------|
    | data availability | excellent for existing aircraft (payload/range diagrams are public) |
    | aircraft payload  | maximum payload possible payload                                    |
    | fuel reserves     | depends on (sometimes unknown) manufacturer assumptions             |
    

    See Also
    --------
    - [Burzlaff (2017), Fig. 3.10](https://www.fzt.haw-hamburg.de/pers/Scholz/arbeiten/TextBurzlaff.pdf)
    - ["Aircraft Payload-Range Analysis for Financiers", Fig. 5 ff.](http://www.aircraftmonitor.com/uploads/1/5/9/9/15993320/aircraft_payload_range_analysis_for_financiers___v2.pdf)

    Returns
    -------
    tuple[ureg.Quantity, ureg.Quantity]
        Fuel burned during flight [mass], Payload mass [mass]

    Raises
    ------
    ValueError
        If the distance is less than zero.
    ValueError
        If the distance exceeds the maximum range of the aircraft as per the payload-range diagram.
    """

    #  all variables of the same dimension must use consistent units
    oew = oew.to('kg')
    mtow = mtow.to('kg')
    payload_point_A = payload_point_A.to('kg')
    payload_point_B = payload_point_B.to('kg')
    range_point_A = range_point_A.to('km')
    range_point_B = range_point_B.to('km')
    range_point_C = range_point_C.to('km')

    acft_weight_point_A = oew + payload_point_A
    acft_weight_point_B = oew + payload_point_B
    acft_weight_point_C = oew

    if d < 0:
        raise ValueError("Distance must be greater than zero.")
    if d < range_point_A:
        slope = (mtow - acft_weight_point_A)/range_point_A
        intercept = acft_weight_point_A
        m_f = (slope * d + intercept) - acft_weight_point_A
        m_pld = payload_point_A
    elif range_point_A <= d < range_point_B:
        slope = (acft_weight_point_B - acft_weight_point_A) / (range_point_B - range_point_A)
        intercept = range_point_A * -slope + acft_weight_point_A
        m_f = mtow - (slope * d + intercept)
        m_pld = (slope * d + intercept) - oew
    elif range_point_B <= d < range_point_C:
        m_f = mtow - acft_weight_point_B # max fuel
        slope = (acft_weight_point_C - acft_weight_point_B) / (range_point_C - range_point_B)
        intercept = range_point_B * -slope + acft_weight_point_B
        m_pld = (slope * d + intercept) - oew
    else:
        raise ValueError("Distance exceeds maximum range of aircraft as per payload-range diagram.")

    return m_f.to('kg'), m_pld.to('kg')