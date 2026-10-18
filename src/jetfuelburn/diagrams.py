import pint
from jetfuelburn import ureg


class payload_range:
    r"""
    Fuel burn estimation from a payload/range diagram.
    """

    @staticmethod
    @ureg.check(
        "[length]",
        "[mass]",
        "[mass]",
        "[length]",
        "[mass]",
        "[length]",
        "[mass]",
        "[length]",
        "[length]",
    )
    def calculate(
        d: pint.Quantity,
        oew: pint.Quantity,
        mtow: pint.Quantity,
        range_point_A: pint.Quantity,
        payload_point_B: pint.Quantity,
        range_point_B: pint.Quantity,
        payload_point_C: pint.Quantity,
        range_point_C: pint.Quantity,
        range_point_D: pint.Quantity,
    ) -> dict[str, pint.Quantity]:
        r"""
        Given aircraft performance parameters from a payload/range diagram and a flight distance $d$,
        calculates the required fuel mass $m_F$ and payload mass $m_{PL}$ for a given mission.

        This function implements the simple _"reading fuel mass off the payload/range diagram directly"_ method:

        ![Payload/Range Diagram](../_static/payload_range_generic.svg)
        Payload/Range diagram of the Airbus A350-900 (data derived [from manufacturer information](https://web.archive.org/web/20211129144142/https://www.airbus.com/sites/g/files/jlcbta136/files/2021-11/Airbus-Commercial-Aircraft-AC-A350-900-1000.pdf)).
        Note that in this figure, the y-axis shows _total_ aircraft weight, not _payload weight_.
        Total aircraft weight can be computed by adding the operating empty weight (OEW) to the payload weight and fuel weight.

        Notes
        -----
        Key assumptions of this fuel calculation function:

        | Parameter         | Assumption                                                          |
        |-------------------|---------------------------------------------------------------------|
        | data availability | excellent for existing aircraft (payload/range diagrams are public) |
        | aircraft payload  | maximum payload possible payload                                    |
        | climb/descent     | implicitly considered                                               |
        | fuel reserves     | depends on (sometimes unknown) manufacturer assumptions             |
        | alternate airport | depends on (sometimes unknown) manufacturer assumptions             |

        Warnings
        --------
        There is no manufacturer-independent convention for including
        reserve and alternate fuel in payload/range diagrams.
        Limited evidence suggests that eg. Boeing always assumes a 200nmi diversion distance (cf. [Slide 43 in this Boeing presentation](https://web.archive.org/web/20250000000000*/http://aviation.itu.edu.tr//img/aviation/datafiles/Lecture%20Notes/FundamentalsofAirlineManagement20152016/Lecture%20Notes/10.1-ITU_Airplane_Performance.pdf) and [this airliners.net discussion](https://www.airliners.net/forum/viewtopic.php?t=764183#p11029989)).
        The user is therefore cautioned against directly comparing aircraft of different manufacturers using this function.

        References
        --------
        - [Burzlaff (2017), Fig. 3.10](https://www.fzt.haw-hamburg.de/pers/Scholz/arbeiten/TextBurzlaff.pdf)
        - ["Aircraft Payload-Range Analysis for Financiers", Fig. 5 ff.](http://www.aircraftmonitor.com/uploads/1/5/9/9/15993320/aircraft_payload_range_analysis_for_financiers___v2.pdf)

        Parameters
        ----------
        d : pint.Quantity
            Flight distance [length]
        oew : pint.Quantity
            Operating Empty Weight (OEW) of the aircraft [mass]
        mtow : pint.Quantity
            Maximum Takeoff Weight (MTOW) of the aircraft [mass]
        range_point_A : pint.Quantity
            Range at point A [length]
        payload_point_B : pint.Quantity
            Payload mass at point B [mass]
        range_point_B : pint.Quantity
            Range at point B [length]
        payload_point_C : pint.Quantity
            Payload mass at point C [mass]
        range_point_C : pint.Quantity
            Range at point C [length]
        range_point_D : pint.Quantity
            Range at point D [length]

        Returns
        -------
        dict[str, pint.Quantity]
            'mass_fuel' : pint.Quantity
                Fuel mass [kg]
            'mass_payload' : pint.Quantity
                Payload mass [kg]

        Raises
        ------
        ValueError
            If any of the input parameters are not [pint](https://pint.readthedocs.io/en/stable/) Quantity instances of the correct dimension.
        ValueError
            If the distance is less than zero.
        ValueError
            If the distance exceeds the maximum range of the aircraft as per the payload-range diagram.

        Example
        -------
        ```pyodide install='jetfuelburn'
        import jetfuelburn
        from jetfuelburn import ureg
        from jetfuelburn.diagrams import payload_range
        payload_range.calculate(
            d=2000*ureg.nmi,
            oew=142.4*ureg.metric_ton,
            mtow=280*ureg.metric_ton,
            range_point_A=500*ureg.nmi,
            payload_point_B=54*ureg.metric_ton,
            range_point_B=5830*ureg.nmi,
            payload_point_C=25*ureg.metric_ton,
            range_point_C=8575*ureg.nmi,
            range_point_D=9620*ureg.nmi,
        )
        ```
        """

        #  all variables of the same dimension must use consistent units
        oew = oew.to("kg")
        mtow = mtow.to("kg")
        payload_point_B = payload_point_B.to("kg")
        payload_point_C = payload_point_C.to("kg")
        range_point_B = range_point_B.to("km")
        range_point_C = range_point_C.to("km")
        range_point_D = range_point_D.to("km")

        acft_weight_point_B = oew + payload_point_B
        acft_weight_point_C = oew + payload_point_C
        acft_weight_point_D = oew

        if d < 0:
            raise ValueError("Distance must be greater than zero.")
        if d < range_point_B:
            slope = (mtow - acft_weight_point_B) / (range_point_B - range_point_A)
            intercept = mtow - slope * range_point_B
            m_f = (slope * d + intercept) - acft_weight_point_B
            m_pld = payload_point_B
        elif range_point_B <= d < range_point_C:
            slope = (acft_weight_point_B - acft_weight_point_C) / (
                range_point_C - range_point_B
            )
            intercept = range_point_B * slope + acft_weight_point_B
            m_f = mtow - (-1 * slope * d + intercept)
            m_pld = (mtow - oew) - m_f
        elif range_point_C <= d < range_point_D:
            m_f = mtow - acft_weight_point_C  # max fuel
            slope = (acft_weight_point_C - acft_weight_point_D) / (
                range_point_D - range_point_C
            )
            intercept = range_point_C * slope + acft_weight_point_C
            m_pld = (-1 * slope * d + intercept) - oew
        else:
            raise ValueError(
                "Distance exceeds maximum range of aircraft as per payload-range diagram."
            )

        return {"mass_fuel": m_f.to("kg"), "mass_payload": m_pld.to("kg")}


# Deprecated alias of the function renamed in jetfuelburn 4.0.0 (to be removed in 5.0.0).
# Accessing the old name raises a DeprecationWarning and returns the new function.
from jetfuelburn.utility.code import _deprecated_module_attribute

_DEPRECATED = {
    "calculate_fuel_consumption_payload_range": (
        "payload_range.calculate",
        payload_range.calculate,
    ),
}


def __getattr__(name):
    return _deprecated_module_attribute(__name__, name, _DEPRECATED)
