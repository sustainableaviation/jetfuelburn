"""Reduced-order fuel burn models, fitted by their authors to simulated or reported flights and keyed by aircraft type."""

import csv
import json
import math
from importlib import resources
import pint
from jetfuelburn import ureg
from jetfuelburn.utility.physics import _calculate_dynamic_pressure


class montlaur_etal:
    r"""
    This class implements the reduced-order fuel burn model of Montlaur et al. (2025):

    ![Montlaur et al. Visual Abstract](../_static/reduced_order_montlaur_etal.svg)

    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the Eurocontrol IMPACT model.

    Fuel burn is calculated according to the function `compute_fuel_ask()` in [the code supplement](https://github.com/luis-uow/emissions_fuel_estimation)
    to Montlaur et al. (2025):

    $$
        F/ASK = \beta_0 + \frac{\beta_1}{D} + \beta_2 D + \beta_3 S + \beta_4 (D \cdot S)
    $$

    where:

    | Symbol         | Unit                                | Description                                                    |
    |----------------|-------------------------------------|----------------------------------------------------------------|
    | $F/ASK$        | [mass] / ([length] $\cdot$ [seats]) | Fuel per Available Seat Kilometer                              |
    | $D$            | [length]                            | Flight distance                                                |
    | $S$            | [dimensionless]                     | Number of available seats                                      |
    | $\beta_{0-4}$  | varies                              | Regression coefficients                                        |

    See Also
    --------
    [`emissions_fuel_estimation.emissions_fuel_model.compute_fuel_ask()`](https://github.com/luis-uow/emissions_fuel_estimation/blob/6d415b38e6089f29ff46a86646db0d5cc04744ba/emissions_fuel_model.py#L9)

    Notes
    -----
    The model differentiates between "Small Aircraft" and "Large Aircraft" based on seat capacity and flight distance,
    as defined in Table 1 of Montlaur et al. (2025):

    | Model Designation | Seat Capacity ($S$)         | Flight Distance ($D$)         | Representative Aircraft                                              |
    |-------------------|-----------------------------|-------------------------------|------------------------------------------------------------------------|
    | "Model D, E"      | $50 \le S \le 172$          | $100 \le D \le 5000$ km       | **CAT D:** B38M, A319<br>**CAT E:** CRJ2, CRJ9, E190                  |
    | "Model B, D"      | $172 \le S \le 365$         | $200 \le D \le 12000$ km      | **CAT B:** A359, A339, B77W, B788, B789<br>**CAT D:** A21N, A20N, B38M |

    References
    ----------
    Montlaur, A., Trapote-Barreira, C., & Delgado, L. (2025).
    Analytical models of flight fuel consumption and Non-CO2 emissions as a function of aircraft capacity.
    _Applied Sciences_, 15(17), 9688.
    doi:[10.3390/app15179688](https://doi.org/10.3390/app15179688)

    Montlaur, A., Delgado, L., & Trapote-Barreira, C. (2021).
    Analytical models for CO2 emissions and travel time for short-to-medium-haul flights considering available seats.
    _Sustainability_, 13(18), 10401.
    doi:[10.3390/su131810401](https://doi.org/10.3390/su131810401)

    Licensing Note
    --------------
    Coefficients from Montlaur et al. (2025), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import montlaur_etal
    result = montlaur_etal.calculate(
        distance=1500 * ureg.km,
        available_seats=180,
    )
    ```
    """

    _REGRESSION_COEFFICIENTS_MODEL_D_E = {
        "intercept": 34.67 * ureg("dimensionless"),
        "inv_dist": 6608.0 * ureg("km"),
        "dist": -1.196e-3 / ureg("km"),
        "seats": -0.1354 * ureg("dimensionless"),
        "interaction": 1.338e-5 / ureg("km"),
    }

    _REGRESSION_COEFFICIENTS_MODEL_B_D = {
        "intercept": 0.7361 * ureg("dimensionless"),
        "inv_dist": 6651.0 * ureg("km"),
        "dist": 5.989e-4 / ureg("km"),
        "seats": 6.152e-2 * ureg("dimensionless"),
        "interaction": -1.014e-6 / ureg("km"),
    }

    @staticmethod
    @ureg.check("[length]", None, None)
    def calculate(
        distance: pint.Quantity,
        available_seats: int,
        model: str = "",
    ) -> pint.Quantity:
        """
        Calculates the estimated fuel consumption per Available Seat Kilometer.

        Parameters
        ----------
        distance : pint.Quantity
            Flight distance [length]
        available_seats : int
            Number of available seats
        model : str, optional
            Model designation to use: `B_D` for large aircraft, `D_E` for small aircraft.
            If left blank, the model will auto-select based on available seats and distance.
            Default is "" (auto-select).

        Returns
        -------
        pint.Quantity
            Estimated fuel consumption [mass/length]

        Raises
        ------
        ValueError
            If inputs are outside the valid operational bounds and model designation is invalid.
        """
        d_km = distance.to("km")

        if not (50 <= available_seats <= 365):
            raise ValueError(
                f"Seats available {available_seats} out of range (50 - 365)."
            )
        if not (100 * ureg.km <= d_km <= 12000 * ureg.km):
            raise ValueError(f"Distance {d_km} out of range (100 - 12,000 km).")
        if d_km > 5000 * ureg.km and available_seats < 172:
            raise ValueError("Flights over 5,000 km require at least 172 seats.")
        if available_seats >= 172 and d_km < 200 * ureg.km:
            raise ValueError(
                "Flights under 200 km are invalid for aircraft with 172+ seats."
            )
        if model not in ("B_D", "D_E") and model != "":
            raise ValueError(
                f"Model '{model}' is not recognized. Use 'B_D', 'D_E', or leave blank for auto-selection based on available seats and distance."
            )

        if model == "":
            if (
                172 <= available_seats <= 365
                and 200 * ureg.km <= d_km <= 12000 * ureg.km
            ):
                model = "B_D"
            else:
                model = "D_E"

        beta: dict = (
            montlaur_etal._REGRESSION_COEFFICIENTS_MODEL_B_D
            if model == "B_D"
            else montlaur_etal._REGRESSION_COEFFICIENTS_MODEL_D_E
        )

        # Fuel/ASK = b0 + b1/D + b2*D + b3*S + b4*D*S
        fuel_ask_value = (
            beta["intercept"]
            + (beta["inv_dist"] / d_km)
            + (beta["dist"] * d_km)
            + (beta["seats"] * available_seats)
            + (beta["interaction"] * d_km * available_seats)
        )

        return fuel_ask_value * ureg("gram / km")


class sacchi_etal:
    r"""
    This class implements the reduced-order fuel burn model of Sacchi et al. (2023):

    ![Sacchi et al. Visual Abstract](../_static/reduced_order_sacchi.svg)

    In this model, fuel burn calculations are based on a weight-based power law.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the European Environmental Agency [EMEP/EEA air pollutant emission inventory guidebook - 2013](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2013)
    which in turn is based on a combination of Eurocontrol BADA flight trajectory simulation model data and the ICAO Engine Emissions Databank (EDB).
    Cruise segment fuel burn is calculated using the [Eurocontrol BADA](https://www.eurocontrol.int/model/bada) model.
    Climb and descent segment fuel burn is calculated using the values provided in the ICAO Engine Emissions Databank.

    Fuel burn is calculated according to Supplement 1 of Sacchi et al. (2023):

    $$
        F_{total} = \eta(t) \cdot \left(
        \underbrace{a_{LTO} \cdot W^{b_{LTO}}}_{\text{LTO}} +
        \underbrace{a_{CD} \cdot W^{b_{CD}}}_{\text{Climb/Descent}} +
        \underbrace{(a_{cruise} \cdot W^{b_{cruise}} + c_{cruise}) \cdot R}_{\text{cruise}}
        \right)
    $$

    where:

    | Symbol         | Dimension         | Description                                                            |
    |----------------|-------------------|------------------------------------------------------------------------|
    | $F_{total}$    | [mass]            | Total fuel consumption of the flight                                   |
    | $W$            | [mass]            | Operating empty weight of the aircraft                                 |
    | $R$            | [length]          | Range of the aircraft (=mission distance)                              |
    | $t$            | [time]            | Scenario year                                                          |
    | $a_{LTO}$      |                   | Coefficient 'a' for LTO phase                                          |
    | $b_{LTO}$      |                   | Exponent 'b' for LTO phase                                             |
    | $a_{CD}$       |                   | Coefficient 'a' for Climb/Descent phase                                |
    | $b_{CD}$       |                   | Exponent 'b' for Climb/Descent phase                                   |
    | $a_{cruise}$   |                   | Coefficient 'a' for Cruise phase                                     |
    | $b_{cruise}$   |                   | Exponent 'b' for Cruise phase                                          |
    | $c_{cruise}$   |                   | Constant 'c' for Cruise phase (fuel per km)                            |
    | $r_{hist}$     | [dimensionless]   | Historical annual improvement rate (2004-2018)                         |
    | $r_{fut}$      | [dimensionless]   | Future annual improvement rate (post-2018)                             |

    Efficiency $\eta(t)$ for years after 2018 is defined through two constant annual improvement factors for the periods 2004-2018 and post-2018:

    $$
        \eta(t) = (1 + r_{hist})^{14} \cdot (1 + r_{fut})^{(t - 2018)}
    $$

    where:

    | Symbol         | Dimension         | Description                                                            |
    |----------------|-------------------|------------------------------------------------------------------------|
    | $\eta(t)$      | [dimensionless]   | Efficiency improvement over 2004 baseline                              |
    | $r_{hist}$     | [dimensionless]   | Historical annual improvement rate (2004-2018)                         |
    | $r_{fut}$      | [dimensionless]   | Projected future annual improvement rate (post-2018)                   |
    | $t$            | [time]            | Scenario year (>=2018)                                                 |

    ![Annual Improvement Plot](../_static/reduced_order_sacchi_improvement.svg)

    Operating empty weight (OEW) is calculated as a function of maximum passenger capacity:

    $$
    OEW = \left(0.0927 \cdot pax_{max}^2 + 253.6 \cdot pax_{max} \cdot (1 - 0.00174)^{(t - 2004)}\right) \; [kg]
    $$

    ![Weight Approximation](../_static/reduced_order_sacchi_weight.svg)

    See Also
    --------
    Cell `DM8` in [Supplement 1 of Sacchi et al. (2020)](https://doi.org/10.5281/zenodo.8059750) for fuel burn in cruise.
    Cell `CQ8` in [Supplement 1 of Sacchi et al. (2020)](https://doi.org/10.5281/zenodo.8059750) for fuel burn in climb/descent.
    Cell `BU8` in [Supplement 1 of Sacchi et al. (2020)](https://doi.org/10.5281/zenodo.8059750) for fuel burn in takeoff/landing.
    Cell `BP8` in [Supplement 1 of Sacchi et al. (2020)](https://doi.org/10.5281/zenodo.8059750) for OEW as a function of max passengers.

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                       |
    |-----------------------|----------------------------------------------------------------------------------|
    | data availability     | approximation of aircraft operating empty weight as a function of max passengers |
    | aircraft payload      | variable                                                                         |
    | climb/descent         | considered implicitly                                                            |
    | reserve fuel uplift   | 45 min for long-haul flights assumed                                             |
    | diversion fuel uplift | not considered                                                                   |

    References
    ----------
    Sacchi, R., Becattini, V., Gabrielli, P., Cox, B., Dirnaichner, A., Bauer, C., & Mazzotti, M. (2023).
    How to make climate-neutral aviation fly. _Nature Communications_. doi:[10.1038/s41467-023-39749-y](https://doi.org/10.1038/s41467-023-39749-y)

    Licensing Note
    --------------
    Coefficients from Sacchi et al. (2023) and its Supplementary Data, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import sacchi_etal
    sacchi_etal.calculate(
        year=2025,
        pax_max=180,
        pax=150,
        R=2200*ureg.km
    )
    ```
    """

    coefficients_LTO = {
        "a": 0.09047379 * (ureg.kg ** (1 - 0.850276476)),
        "b": 0.850276476,  # Dimensionless exponent
    }

    coefficients_CD = {
        "a": 1.144010778 * (ureg.kg ** (1 - 0.5374018)),
        "b": 0.5374018,  # Dimensionless exponent
    }

    coefficients_cruise = {
        "a": 5.8583e-05 * (ureg.kg ** (1 - 0.976183654)) / ureg.km,
        "b": 0.976183654,  # Dimensionless exponent
        "c": 0.783563064 * ureg.kg / ureg.km,
    }
    historical_improvement_rate = -0.006
    future_improvement_rate = -0.008

    @staticmethod
    @ureg.check(None, "[mass]", "[length]")  # year  # TOW  # R
    def _calculate_single_pass(
        year: int,
        TOW: pint.Quantity,
        R: pint.Quantity,
    ) -> pint.Quantity:
        """
        Helper function to calculate fuel for a specific given takeoff weight $TOW$ (including fuel).
        """
        if year < 2018:
            raise ValueError("Year must be 2018 or later.")

        eff_factor_hist = (1 + sacchi_etal.historical_improvement_rate) ** (2018 - 2004)
        years_post_2018 = year - 2018
        eff_factor_future = (1 + sacchi_etal.future_improvement_rate) ** years_post_2018
        total_efficiency_factor = eff_factor_hist * eff_factor_future

        lto_fuel_base = sacchi_etal.coefficients_LTO["a"] * (
            TOW ** sacchi_etal.coefficients_LTO["b"]
        )
        cd_fuel_base = sacchi_etal.coefficients_CD["a"] * (
            TOW ** sacchi_etal.coefficients_CD["b"]
        )
        cruise_rate_per_km = (
            sacchi_etal.coefficients_cruise["a"]
            * (TOW ** sacchi_etal.coefficients_cruise["b"])
            + sacchi_etal.coefficients_cruise["c"]
        )
        cruise_fuel_base = cruise_rate_per_km * R

        return (
            lto_fuel_base + cd_fuel_base + cruise_fuel_base
        ) * total_efficiency_factor

    @classmethod
    @ureg.check(
        None,  # cls
        None,  # year
        None,  # pax_max
        None,  # pax
        "[length]",  # R
        "[time]",  # reserve
        "[mass]",  # tolerance
        None,  # max_iterations
    )
    def calculate(
        cls,
        year: int,
        pax_max: int,
        pax: int,
        R: pint.Quantity,
        reserve: pint.Quantity = 45 * ureg("min"),
        tolerance: pint.Quantity = 100 * ureg("kg"),
        max_iterations: int = 20,
    ) -> pint.Quantity:
        """
        Calculates the required fuel mass iteratively.

        Since Fuel depends on Take-Off Weight (TOW), and TOW includes Fuel,
        this method iterates until the fuel mass converges.

        Parameters
        ----------
        year : int
            Scenario year (>=2018).
        pax_max : int
            Maximum passenger capacity of the aircraft.
        pax : int
            Number of passengers on board (assumed to weigh 110kg incl. luggage each).
        R : pint.Quantity
            Mission range [length].
        reserve : pint.Quantity, optional
            Reserve fuel, given as flight time at an assumed cruise speed of 800 km/h [time].
            Default is 45 min.
        tolerance : pint.Quantity, optional
            Convergence tolerance for fuel mass [mass]. Default is 100 kg.
        max_iterations : int, optional
            Maximum number of iterations. Default is 20.

        Returns
        -------
        pint.Quantity
            Total fuel mass [kg].
        """
        if year < 2018:
            raise ValueError("Year must be 2018 or later.")
        if pax < 0 or pax > pax_max:
            raise ValueError(
                f"Number of passengers must be between 0 and maximum pax {pax_max}."
            )

        OEW = (
            0.0927 * pax_max**2 + 253.6 * pax_max * (1 - 0.00174) ** (year - 2004)
        ) * ureg("kg")
        payload = pax * 110 * ureg("kg")
        R = R.to("km") + reserve.to("hr") * 800 * ureg(
            "km/hr"
        )  # add reserve distance (assuming 800km/h cruise speed)

        fuel_guess = 0.0 * ureg(
            "kg"
        )  # initial guess: fuel is 0, or a small fraction of weight

        for i in range(max_iterations):
            current_TOW = OEW + payload + fuel_guess

            new_fuel = cls._calculate_single_pass(year, current_TOW, R)

            if abs(new_fuel - fuel_guess) < tolerance:
                return new_fuel

            fuel_guess = new_fuel

        raise RuntimeError(
            f"Fuel calculation did not converge after {max_iterations} iterations."
        )


class yanto_etal:
    r"""
    This class implements the reduced-order fuel burn model of Yanto and Liem (2017):

    ![Yanto and Liem Visual Abstract](../_static/reduced_order_yanto_etal.svg)

    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from a combination of Eurocontrol BADA flight trajectory simulation model and the Breguet range equation.
    Climb and descent segment fuel burn is calculated using the [Eurocontrol BADA](https://www.eurocontrol.int/model/bada) model.
    Cruise segment fuel burn is calculated using the Breguet range equation.

    Fuel burn is calculated according to Table 5 in Yanto and Liem (2017):

    $$
        W_f = c_R \cdot R + c_P \cdot PL + c_C
    $$

    where:

    | Symbol     | Dimension         | Description                                                            |
    |------------|-------------------|------------------------------------------------------------------------|
    | $W_f$      | [mass]            | Fuel required for the mission of the aircraft                          |
    | $R$        | [distance]        | Range of the aircraft (=mission distance)                              |
    | $PL$       | [mass]            | Payload mass of the aircraft                                           |
    | $c_R$      | [mass/distance]   | Regression coefficient for range                                       |
    | $c_P$      | [mass/mass]       | Regression coefficient for payload                                     |
    | $c_C$      | [mass]            | Constant term                                                          |

    Warnings
    --------
    The x-axes of all three panels in Figure 14 of Yanto and Liem (2017) are incorrectly rendered.
    According to panel (a), the maximum achievable range of a Boeing 777 would be ~30'000NM. This is ~1.6x the circumference of the Earth.
    Neither assuming that the axis multiplier `1e4` nor the unit `nm` (sic!) are incorrect explains this issue.
    Figure 5 was instead used to test the implementation of the method.

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                  |
    |-----------------------|-----------------------------------------------------------------------------|
    | data availability     | 37 selected aircraft                                                        |
    | aircraft payload      | variable                                                                    |
    | climb/descent         | considered implicitly                                                       |
    | reserve fuel uplift   | assumed constant at _"0.08 zero-fuel weight"_ (cf. P.577)                   |
    | diversion fuel uplift | unknown                                                                     |

    References
    ----------
    Yanto, J., & Liem, R. P. (2017).
    Efficient fast approximation for aircraft fuel consumption for decision-making and policy analysis.
    In _AIAA Modeling and Simulation Technologies Conference_ (p. 3338).
    doi:[10.2514/6.2017-3338](https://doi.org/10.2514/6.2017-3338)

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import yanto_etal
    yanto_etal.list_aircraft()[0:10]
    yanto_etal.calculate(
        acft='A321',
        R=2200*ureg.km,
        PL=18*ureg.metric_ton
    )
    ```
    """

    _regression_coefficients = {
        "A319": {"c_R": 1.809, "c_P": 0.145, "c_C": 580.83},
        "A320": {"c_R": 1.984, "c_P": 0.138, "c_C": 390.97},
        "A332": {"c_R": 8.305, "c_P": 0.341, "c_C": -2314.39},
        "A333": {"c_R": 8.278, "c_P": 0.329, "c_C": 706.80},
        "B731": {"c_R": 2.085, "c_P": 0.148, "c_C": 125.44},
        "B733": {"c_R": 2.099, "c_P": 0.146, "c_C": 470.24},
        "B734": {"c_R": 2.412, "c_P": 0.16, "c_C": 431.29},
        "B735": {"c_R": 1.825, "c_P": 0.117, "c_C": 631.40},
        "B736": {"c_R": 1.922, "c_P": 0.185, "c_C": 517.48},
        "B737": {"c_R": 2.063, "c_P": 0.165, "c_C": 915.72},
        "B738": {"c_R": 2.539, "c_P": 0.157, "c_C": 484.68},
        "B739": {"c_R": 2.507, "c_P": 0.172, "c_C": 503.32},
        "B739ER": {"c_R": 2.547, "c_P": 0.18, "c_C": 328.96},
        "B752": {"c_R": 2.966, "c_P": 0.168, "c_C": 443.28},
        "B753": {"c_R": 3.242, "c_P": 0.177, "c_C": 762.16},
        "B772": {"c_R": 6.724, "c_P": 0.396, "c_C": -7634.59},
        "B773": {"c_R": 8.163, "c_P": 0.371, "c_C": -8576.72},
        "CRJ2": {"c_R": 1.045, "c_P": 0.116, "c_C": 140.42},
        "CRJ9": {"c_R": 1.271, "c_P": 0.141, "c_C": 778.27},
        "E145": {"c_R": 0.705, "c_P": 0.134, "c_C": 601.88},
        "MD80": {"c_R": 2.463, "c_P": 0.152, "c_C": -67.81},
        "A318": {"c_R": 1.407, "c_P": 0.172, "c_C": 17.29},
        "A321": {"c_R": 2.61, "c_P": 0.176, "c_C": 880.53},
        "A343": {"c_R": 8.81, "c_P": 0.424, "c_C": -5057.09},
        "A345": {"c_R": 10.86, "c_P": 0.453, "c_C": -9708.52},
        "A342": {"c_R": 8.36, "c_P": 0.348, "c_C": -290.49},
        "A346": {"c_R": 12.428, "c_P": 0.385, "c_C": -8552.62},
        "B742": {"c_R": 10.06, "c_P": 0.403, "c_C": -8964.48},
        "B744": {"c_R": 8.779, "c_P": 0.247, "c_C": -9191.53},
        "B762": {"c_R": 4.102, "c_P": 0.228, "c_C": 716.20},
        "B763": {"c_R": 5.159, "c_P": 0.279, "c_C": -2282.61},
        "CRJ7": {"c_R": 1.194, "c_P": 0.143, "c_C": 725.06},
        "CRJ1": {"c_R": 0.781, "c_P": 0.169, "c_C": 351.56},
        "E140": {"c_R": 0.673, "c_P": 0.133, "c_C": 633.03},
        "E170": {"c_R": 1.19, "c_P": 0.144, "c_C": 949.164},
        "E190": {"c_R": 1.626, "c_P": 0.145, "c_C": 1219.34},
        "MD90": {"c_R": 2.157, "c_P": 0.117, "c_C": 643.18},
    }

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(yanto_etal._regression_coefficients.keys())

    @staticmethod
    @ureg.check(
        None,  # acft
        "[length]",
        "[mass]",
    )
    def calculate(
        acft: str,
        R: pint.Quantity,
        PL: pint.Quantity,
    ) -> pint.Quantity:
        """
        Given an ICAO aircraft designator, mission range and payload mass, calculates the fuel burned.

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator
        R : pint.Quantity
            Mission range [length]
        PL : pint.Quantity
            Payload mass [mass]

        Returns
        -------
        pint.Quantity
            Fuel mass [kg]

        Raises
        ------
        ValueError
            If the ICAO aircraft designator is not found in the model data.
        ValueError
            If range or payload are less than zero.
        """
        if R < 0:
            raise ValueError("Range must be greater than zero.")
        if PL < 0:
            raise ValueError("Payload mass must be greater than zero.")
        if acft not in yanto_etal._regression_coefficients.keys():
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data. Please select one of the following: {yanto_etal._regression_coefficients.keys()}"
            )

        R = R.to("km").magnitude
        PL = PL.to("kg").magnitude

        m_f = (
            yanto_etal._regression_coefficients[acft]["c_R"] * R
            + yanto_etal._regression_coefficients[acft]["c_P"] * PL
            + yanto_etal._regression_coefficients[acft]["c_C"]
        )

        return m_f * ureg("kg")


class lee_etal:
    """
    This class implements the reduced-order fuel burn model of Lee et al. (2010).

    ![Lee et al. Visual Abstract](../_static/reduced_order_lee_etal.svg)

    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from a combination of Eurocontrol BADA flight trajectory simulation model and the Breguet range equation.
    Climb segment fuel burn is calculated using the [Eurocontrol BADA](https://www.eurocontrol.int/model/bada) model.
    Descent segment fuel burn is assumed equal to cruise segment fuel burn.
    Cruise segment fuel burn is calculated using the Breguet range equation.

    For the equations implemented in this class, see Lee et al. (2010), Eqns.(13)ff. and Figure 5.

    Warnings
    --------

    Note that the present implementation of the Lee et al. (2010)
    cannot completely replicate aircraft payload in a small segment of Figure 6 in referenced paper.
    The calculated aircraft payload for extreme aircraft ranges differs from the one shown in the paper:

    ```python exec="true" html="true"
    from jetfuelburn.figures.reducedorder import figure_lee2010
    fig = figure_lee2010()
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    # https://pawamoy.github.io/markdown-exec/gallery/#with-plotly
    ```

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                            |
    |-----------------------|-------------------------------------------------------|
    | data availability     | 21 selected aircraft                                  |
    | aircraft payload      | variable                                              |
    | climb/descent         | considered implicitly                                 |
    | reserve fuel uplift   | assumed constant at 0.08 zero-fuel weight (cf. P.4)   |
    | diversion fuel uplift | unclear (cf. P.4)                                     |

    References
    ----------
    Lee, H. T., & Chatterji, G. (2010, September).
    Closed-form takeoff weight estimation model for air transportation simulation.
    In _10th AIAA Aviation Technology, Integration, and Operations (ATIO) Conference_ (p. 9156).
    doi:[10.2514/6.2010-9156](https://doi.org/10.2514/6.2010-9156)

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import lee_etal
    lee_etal.list_aircraft()[0:10]
    lee_etal.calculate(
        acft='B732',
        W_E=265825*ureg.N,
        W_MPLD=156476*ureg.N,
        W_MTO=513422*ureg.N,
        W_MF=142365*ureg.N,
        S=91.09*ureg.m ** 2,
        C_D0=0.0214,
        C_D2=0.0462,
        c=(2.131E-4)/ureg.s,
        h=9144*ureg.m,
        V=807.65*ureg.kph,
        d=2000*ureg.nmi
    )
    ```
    """

    _regression_coefficients = {
        "FA50": {
            "k_1": -18.2e-12,
            "k_2": 3.11e-9,
            "k_3": -163e-9,
            "k_4": 2.46e-6,
            "k_5": 47.1e-6,
            "k_6": -0.823e-3,
        },
        "E145": {
            "k_1": 17.3e-12,
            "k_2": 4.72e-9,
            "k_3": -286e-9,
            "k_4": 0.0268e-6,
            "k_5": 77.5e-6,
            "k_6": -1.36e-3,
        },
        "CRJ1": {
            "k_1": 9.74e-12,
            "k_2": 1.11e-9,
            "k_3": 133e-9,
            "k_4": 1.07e-6,
            "k_5": -70.4e-6,
            "k_6": 8.14e-3,
        },
        "A319": {
            "k_1": 20.7e-12,
            "k_2": -1.07e-9,
            "k_3": 107e-9,
            "k_4": 1.10e-6,
            "k_5": -46.3e-6,
            "k_6": 5.91e-3,
        },
        "A320": {
            "k_1": 29.4e-12,
            "k_2": -2.63e-9,
            "k_3": 64.2e-9,
            "k_4": 1.40e-6,
            "k_5": -22.5e-6,
            "k_6": 3.74e-3,
        },
        "A332": {
            "k_1": 30.6e-12,
            "k_2": -2.85e-9,
            "k_3": 70.0e-9,
            "k_4": 1.31e-6,
            "k_5": -21.5e-6,
            "k_6": 3.29e-3,
        },
        "B712": {
            "k_1": -31.4e-12,
            "k_2": 4.62e-9,
            "k_3": -238e-9,
            "k_4": 0.552e-6,
            "k_5": 68.6e-6,
            "k_6": -3.34e-3,
        },
        "B732": {
            "k_1": -42.7e-12,
            "k_2": 5.64e-9,
            "k_3": -310e-9,
            "k_4": 0.929e-6,
            "k_5": 91.2e-6,
            "k_6": -4.61e-3,
        },
        "B733": {
            "k_1": -23.7e-12,
            "k_2": 3.96e-9,
            "k_3": -248e-9,
            "k_4": 0.680e-6,
            "k_5": 75.5e-6,
            "k_6": -4.53e-3,
        },
        "B737": {
            "k_1": 38.9e-12,
            "k_2": -3.37e-9,
            "k_3": 130e-9,
            "k_4": 1.48e-6,
            "k_5": -43.6e-6,
            "k_6": 5.81e-3,
        },
        "B738": {
            "k_1": 31.1e-12,
            "k_2": -2.75e-9,
            "k_3": 115e-9,
            "k_4": 1.47e-6,
            "k_5": -40.3e-6,
            "k_6": 5.12e-3,
        },
        "B744": {
            "k_1": 8.45e-12,
            "k_2": -0.816e-9,
            "k_3": 44.4e-9,
            "k_4": 1.03e-6,
            "k_5": -15.7e-6,
            "k_6": 1.60e-3,
        },
        "B752": {
            "k_1": -20.2e-12,
            "k_2": 4.28e-9,
            "k_3": -264e-9,
            "k_4": 0.447e-6,
            "k_5": 78.4e-6,
            "k_6": -5.40e-3,
        },
        "B763": {
            "k_1": -35.6e-12,
            "k_2": 5.67e-9,
            "k_3": -279e-9,
            "k_4": 0.180e-6,
            "k_5": 86.3e-6,
            "k_6": -5.04e-3,
        },
        "B772": {
            "k_1": 21.9e-12,
            "k_2": -2.84e-9,
            "k_3": 65.0e-9,
            "k_4": 1.38e-6,
            "k_5": -17.1e-6,
            "k_6": 2.56e-3,
        },
        "MD82": {
            "k_1": -58.9e-12,
            "k_2": 8.29e-9,
            "k_3": -364e-9,
            "k_4": 0.290e-6,
            "k_5": 106e-6,
            "k_6": -5.48e-3,
        },
        "MD83": {
            "k_1": -30.0e-12,
            "k_2": 4.55e-9,
            "k_3": -289e-9,
            "k_4": 0.802e-6,
            "k_5": 87.5e-6,
            "k_6": -5.64e-3,
        },
        "JS31": {
            "k_1": 38.4e-12,
            "k_2": -15.2e-9,
            "k_3": -612e-9,
            "k_4": 2.46e-6,
            "k_5": 1.61e-6,
            "k_6": -10.6e-3,
        },
        "SF34": {
            "k_1": -59.8e-12,
            "k_2": 7.70e-9,
            "k_3": -374e-9,
            "k_4": 1.98e-6,
            "k_5": 58.7e-6,
            "k_6": -2.98e-3,
        },
        "E120": {
            "k_1": 25.7e-12,
            "k_2": -1.40e-9,
            "k_3": -353e-9,
            "k_4": 1.01e-6,
            "k_5": 82.5e-6,
            "k_6": -4.55e-3,
        },
        "AT45": {
            "k_1": 29.7e-12,
            "k_2": -6.41e-9,
            "k_3": -244e-9,
            "k_4": 1.41e-6,
            "k_5": 63.7e-6,
            "k_6": -3.96e-3,
        },
    }

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(lee_etal._regression_coefficients.keys())

    @staticmethod
    @ureg.check(
        None,  # acft
        "[force]",  # W_E
        "[force]",  # W_MPLD
        "[force]",  # W_MTO
        "[force]",  # W_MF
        "[area]",  # S
        "[]",  # C_D0
        "[]",  # C_D2
        "1/[time]",  # c
        "[length]",  # h
        "[speed]",  # V
        "[length]",  # d
    )
    def calculate(
        acft: str,
        W_E: pint.Quantity,
        W_MPLD: pint.Quantity,
        W_MTO: pint.Quantity,
        W_MF: pint.Quantity,
        S: pint.Quantity,
        C_D0: float | pint.Quantity,
        C_D2: float | pint.Quantity,
        c: pint.Quantity,
        h: pint.Quantity,
        V: pint.Quantity,
        d: pint.Quantity,
    ) -> dict[str, pint.Quantity]:
        """
        Given an ICAO aircraft designator, the aircraft weights, drag polar and engine parameters,
        the cruise altitude and speed, and the flight distance, calculates the fuel mass and the payload mass of the mission.

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator
        W_E : pint.Quantity
            Aircraft empty weight [weight] (not mass !)
        W_MPLD : pint.Quantity
            Aircraft maximum payload [weight] (not mass !)
        W_MTO : pint.Quantity
            Aircraft maximum takeoff weight [weight] (not mass !)
        W_MF : pint.Quantity
            Aircraft maximum fuel weight [weight] (not mass !)
        S : pint.Quantity
            Aircraft wing area [area]
        C_D0 : float | pint.Quantity
            Parasitic drag coefficient [dimensionless]
        C_D2 : float | pint.Quantity
            Induced drag coefficient [dimensionless]
        c : pint.Quantity
            Thrust specific fuel consumption [1/time]
        h : pint.Quantity
            Cruise altitude [length]
        V : pint.Quantity
            Cruise speed [speed]
        d : pint.Quantity
            wind-compensated distance [length]

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
            If the ICAO aircraft designator is not found in the model data.
        ValueError
            If any parameter is less than zero.
        """
        parameters = [W_E, W_MPLD, W_MTO, W_MF, S, C_D0, C_D2, c, h, V, d]
        if any(param <= 0 for param in parameters):
            raise ValueError("All parameters must be greater than zero.")
        if acft not in lee_etal._regression_coefficients.keys():
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data. Please select one of the following: {lee_etal._regression_coefficients.keys()}"
            )

        q = _calculate_dynamic_pressure(speed=V, altitude=h)
        q = q.to("N/m^2").magnitude
        c = c.magnitude
        S = S.to("m^2").magnitude
        W_E = W_E.magnitude
        W_MPLD = W_MPLD.magnitude
        W_MTO = W_MTO.magnitude
        W_MF = W_MF.magnitude
        d = d.to("m").magnitude
        h = h.to("m").magnitude
        V = V.to("m/s").magnitude

        f_res = 0.08  # cf. Section II D of Lee et al.
        f_man = 0.007  # cf. Section II D of Lee et al.
        f_inc = (
            lee_etal._regression_coefficients[acft]["k_1"] * h**2
            + lee_etal._regression_coefficients[acft]["k_2"] * h * V
            + lee_etal._regression_coefficients[acft]["k_3"] * V**2
            + lee_etal._regression_coefficients[acft]["k_4"] * h
            + lee_etal._regression_coefficients[acft]["k_5"] * V
            + lee_etal._regression_coefficients[acft]["k_6"]
        )

        A_1 = (1 / (q * S)) * math.sqrt(C_D2 / C_D0)  # Eqn.(14) in Lee et al.
        A_2 = (c / V) * math.sqrt(C_D2 * C_D0)  # Eqn.(15) in Lee et al.
        A_d = math.tan(A_2 * d)  # Eqn.(16) in Lee et al.
        A_3 = f_inc + f_man  # Eqn.(18) in Lee et al.
        A_4 = 1 + f_res  # Eqn.(19) in Lee et al.
        W_MZF = (-A_1 * A_3 * A_d * W_MTO**2 + (1 - A_3) * W_MTO - (A_d / A_1)) / (
            A_4 * (A_1 * A_d * W_MTO + 1)
        )  # Eqn.(20) in Lee et al.

        if W_E + W_MPLD < W_MZF:  # Figure 5(b) in Lee et al.
            W_PLD = W_MPLD  # Figure 5(d) in Lee et al.
            W_ZF = W_E + W_PLD  # Figure 5(d) in Lee et al.
            # quadratic formula ax^2 + bx + c = 0
            a = A_1 * A_3 * A_d
            b = A_1 * A_4 * A_d * W_ZF + A_3 - 1
            c = A_4 * W_ZF + (A_d / A_1)
            W_TO = (-b + math.sqrt(b**2 - 4 * a * c)) / (
                2 * a
            )  # Eqn.(17) in Lee et al.
            W_F = W_TO - W_PLD
        else:
            W_F = W_MTO - W_MZF  # Figure 5(c) in Lee et al.
            if W_F < W_MF:  # Figure 5(e) in Lee et al.
                W_PLD = W_MZF - W_E
            else:  # Figure 5(g) in Lee et al.
                # quadratic formula ax^2 + bx + c = 0
                a = A_1 * A_d * (A_3 + A_4)  # Eqn.(22) in Lee et al.
                b = (
                    2 * A_1 * A_d * (A_3 + A_4) * W_E
                    + A_1 * A_d * (2 * A_3 + A_4) * W_MF
                    + A_3
                    + A_4
                    - 1
                )  # Eqn.(23) in Lee et al.
                c = (
                    A_1 * A_d * (A_3 + A_4) * W_E**2
                    + A_1 * A_d * (2 * A_3 + A_4) * W_E * W_MF
                    + A_1 * A_3 * A_d * W_MF**2
                    + (A_3 + A_4 - 1) * W_E
                    + (A_3 - 1) * W_MF
                    + (A_d / A_1)
                )  # Eqn.(24) in Lee et al.
                W_PLD = (-b + math.sqrt(b**2 - 4 * a * c)) / (
                    2 * a
                )  # Eqn.(21) in Lee et al.

        g = 9.8067 * (ureg.m / ureg.s**2)
        m_f = (W_F * ureg.N) / g
        m_pld = (W_PLD * ureg.N) / g

        return {"mass_fuel": m_f.to("kg"), "mass_payload": m_pld.to("kg")}


class seymour_etal:
    r"""
    Reduced-order fuel burn model based on Seymour et al. (2020).

    ![Seymour et al. Visual Abstract](../_static/reduced_order_seymour_etal.svg)

    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were fitted to simulated flight missions: climb, cruise, descent, approach and landing
    follow from BADA-based flight profile simulations, and taxi and take-off fuel flow from engine test data
    (ICAO Engine Emissions Databank for jets, FOCA database for piston engines) or from BADA.

    Fuel burn is calculated according to Table M.7 in the supplement to Seymour et al. (2020):

    $$
        F=a_1 \cdot R^2 + a_2 \cdot R + c
    $$

    where:

    | Symbol     | Dimension            | Description                                          |
    |------------|----------------------|------------------------------------------------------|
    | $F$        | [mass]               | Fuel required for the mission of the aircraft        |
    | $R$        | [distance]           | Great-circle distance between origin and destination |
    | $a_1$      | [mass/distance²]     | Regression coefficient for distance squared          |
    | $a_2$      | [mass/distance]      | Regression coefficient for distance                  |
    | $c$        | [mass]               | Constant term                                        |

    $R$ is the great-circle distance $d_{gc}$ of Eq. 7 in Seymour et al. (2020).
    The simulated missions behind the fit include average route inefficiency:
    Eq. 6 of the paper sets their flight path distance to $d_{fp} = 1.0387 \cdot d_{gc} + 40.5$ km.

    The coefficients are transcribed from Table M.7 of the Supplementary Information, the paper's published fit
    (the FEAT GitHub `.csv` file holds an earlier fit, committed in June 2020).

    Warnings
    --------
    Each fit is based on 25 simulated missions between 200 km (or the type's shortest distance in the OAG data, if longer)
    and the type's maximum range in Table L.6 of the Supplementary Information (e.g. 5,803 km for the B738).
    Results beyond that range are extrapolations. For the 26 types with a negative $a_1$, the fit bends downward
    beyond that range. Where the fit no longer returns a positive fuel burn, `calculate()` raises a `ValueError`.

    Note that Seymour et al. in the Disclaimers section of their publication mention, that:
    > This document has been created with elements of Base of Aircraft Data (BADA) Family 3 Release 3.15
    > which has been made available by EUROCONTROL to ETH Zurich (...). EUROCONTROL has all relevant rights to BADA.
    > (...) The fuel burn models provided in SI M [Section M of the Supplementary Information, which holds Table M.7]
    > shall not be used for comparing fuel efficiency and emission data between aircraft models and manufacturers.
    > Recommended model applications are reported in Section 3.5.

    Section 3.5 then mentions as potential applications:
    > (...) computing global CO2 emissions using the reduced order models (...) [and]
    > (...) fleet turnover and flight route projections can be combined to create any
    > number of future flight movement scenarios which together with the reduced order models can be leveraged to generate valuable insights.

    See Also
    --------
    [FEAT repository on GitHub](https://github.com/kwdseymour/FEAT/tree/master):
    Jupyter notebooks and `.csv` files that accompany the paper.

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                  |
    |-----------------------|-----------------------------------------------------------------------------|
    | data availability     | 133 selected aircraft                                                       |
    | aircraft payload      | assumed to be average for each aircraft type                                |
    | climb/descent         | considered implicitly                                                       |
    | route inefficiency    | considered implicitly, according to Eq. 6 of Seymour et al. (2020)          |
    | reserve fuel uplift   | considered implicitly, according to ICAO requirements                       |
    | diversion fuel uplift | considered implicitly, according to ICAO requirements                       |

    References
    ----------
    Seymour, K., Held, M., Georges, G., & Boulouchos, K. (2020).
    Fuel Estimation in Air Transportation: Modeling global fuel consumption for commercial aviation.
    _Transportation Research Part D: Transport and Environment_, 88, 102528.
    doi:[10.1016/j.trd.2020.102528](https://doi.org/10.1016/j.trd.2020.102528)

    Licensing Note
    --------------
    Coefficients from Table M.7 of the Supplementary Information of Seymour et al. (2020), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import seymour_etal
    seymour_etal.list_aircraft()[0:10]
    seymour_etal.calculate(
        acft='A321',
        R=2200*ureg.km,
    )
    ```
    """

    _regression_coefficients = {
        "A140": {
            "reduced_fuel_a1": 1.57e-4,
            "reduced_fuel_a2": 1.30,
            "reduced_fuel_intercept": 160,
        },
        "A148": {
            "reduced_fuel_a1": 6.38e-5,
            "reduced_fuel_a2": 1.76,
            "reduced_fuel_intercept": 999,
        },
        "A158": {
            "reduced_fuel_a1": 2.79e-5,
            "reduced_fuel_a2": 2.58,
            "reduced_fuel_intercept": 819,
        },
        "A20N": {
            "reduced_fuel_a1": 5.52e-5,
            "reduced_fuel_a2": 2.39,
            "reduced_fuel_intercept": 1008,
        },
        "A21N": {
            "reduced_fuel_a1": 7.07e-5,
            "reduced_fuel_a2": 2.70,
            "reduced_fuel_intercept": 1206,
        },
        "A306": {
            "reduced_fuel_a1": 2.22e-4,
            "reduced_fuel_a2": 5.22,
            "reduced_fuel_intercept": 2703,
        },
        "A30B": {
            "reduced_fuel_a1": 1.99e-4,
            "reduced_fuel_a2": 6.50,
            "reduced_fuel_intercept": 2491,
        },
        "A310": {
            "reduced_fuel_a1": 1.74e-4,
            "reduced_fuel_a2": 4.31,
            "reduced_fuel_intercept": 2432,
        },
        "A318": {
            "reduced_fuel_a1": 6.43e-5,
            "reduced_fuel_a2": 2.37,
            "reduced_fuel_intercept": 1175,
        },
        "A319": {
            "reduced_fuel_a1": 7.70e-5,
            "reduced_fuel_a2": 2.32,
            "reduced_fuel_intercept": 1280,
        },
        "A320": {
            "reduced_fuel_a1": 1.25e-4,
            "reduced_fuel_a2": 2.47,
            "reduced_fuel_intercept": 1374,
        },
        "A321": {
            "reduced_fuel_a1": -5.88e-5,
            "reduced_fuel_a2": 4.09,
            "reduced_fuel_intercept": 1182,
        },
        "A332": {
            "reduced_fuel_a1": 1.75e-4,
            "reduced_fuel_a2": 4.91,
            "reduced_fuel_intercept": 3727,
        },
        "A333": {
            "reduced_fuel_a1": 2.51e-5,
            "reduced_fuel_a2": 6.53,
            "reduced_fuel_intercept": 2232,
        },
        "A339": {
            "reduced_fuel_a1": 1.77e-4,
            "reduced_fuel_a2": 4.64,
            "reduced_fuel_intercept": 4219,
        },
        "A342": {
            "reduced_fuel_a1": 2.47e-4,
            "reduced_fuel_a2": 5.06,
            "reduced_fuel_intercept": 4951,
        },
        "A343": {
            "reduced_fuel_a1": 2.62e-4,
            "reduced_fuel_a2": 5.50,
            "reduced_fuel_intercept": 3989,
        },
        "A345": {
            "reduced_fuel_a1": 2.27e-4,
            "reduced_fuel_a2": 6.72,
            "reduced_fuel_intercept": 5302,
        },
        "A346": {
            "reduced_fuel_a1": 2.60e-4,
            "reduced_fuel_a2": 6.85,
            "reduced_fuel_intercept": 5646,
        },
        "A359": {
            "reduced_fuel_a1": 8.57e-5,
            "reduced_fuel_a2": 6.16,
            "reduced_fuel_intercept": 1803,
        },
        "A35K": {
            "reduced_fuel_a1": 1.85e-4,
            "reduced_fuel_a2": 5.38,
            "reduced_fuel_intercept": 4483,
        },
        "A388": {
            "reduced_fuel_a1": 2.96e-4,
            "reduced_fuel_a2": 11.43,
            "reduced_fuel_intercept": 6565,
        },
        "AJ27": {
            "reduced_fuel_a1": 1.13e-4,
            "reduced_fuel_a2": 2.22,
            "reduced_fuel_intercept": 924,
        },
        "AN24": {
            "reduced_fuel_a1": 6.24e-5,
            "reduced_fuel_a2": 1.60,
            "reduced_fuel_intercept": 209,
        },
        "AN38": {
            "reduced_fuel_a1": 3.00e-5,
            "reduced_fuel_a2": 1.51,
            "reduced_fuel_intercept": 60,
        },
        "AT43": {
            "reduced_fuel_a1": 2.04e-4,
            "reduced_fuel_a2": 0.80,
            "reduced_fuel_intercept": 199,
        },
        "AT72": {
            "reduced_fuel_a1": 2.55e-4,
            "reduced_fuel_a2": 1.14,
            "reduced_fuel_intercept": 201,
        },
        "ATP": {
            "reduced_fuel_a1": 4.76e-4,
            "reduced_fuel_a2": 0.98,
            "reduced_fuel_intercept": 239,
        },
        "B190": {
            "reduced_fuel_a1": 3.63e-5,
            "reduced_fuel_a2": 0.70,
            "reduced_fuel_intercept": 82,
        },
        "B38M": {
            "reduced_fuel_a1": 3.90e-5,
            "reduced_fuel_a2": 2.30,
            "reduced_fuel_intercept": 993,
        },
        "B39M": {
            "reduced_fuel_a1": 5.21e-5,
            "reduced_fuel_a2": 2.18,
            "reduced_fuel_intercept": 1160,
        },
        "B461": {
            "reduced_fuel_a1": 1.87e-4,
            "reduced_fuel_a2": 2.58,
            "reduced_fuel_intercept": 1066,
        },
        "B462": {
            "reduced_fuel_a1": 9.39e-5,
            "reduced_fuel_a2": 2.74,
            "reduced_fuel_intercept": 1045,
        },
        "B463": {
            "reduced_fuel_a1": 2.41e-4,
            "reduced_fuel_a2": 2.71,
            "reduced_fuel_intercept": 1140,
        },
        "B712": {
            "reduced_fuel_a1": 9.54e-5,
            "reduced_fuel_a2": 2.56,
            "reduced_fuel_intercept": 935,
        },
        "B722": {
            "reduced_fuel_a1": 2.32e-4,
            "reduced_fuel_a2": 4.94,
            "reduced_fuel_intercept": 1938,
        },
        "B732": {
            "reduced_fuel_a1": 1.49e-5,
            "reduced_fuel_a2": 3.33,
            "reduced_fuel_intercept": 1208,
        },
        "B733": {
            "reduced_fuel_a1": -2.03e-5,
            "reduced_fuel_a2": 3.41,
            "reduced_fuel_intercept": 824,
        },
        "B734": {
            "reduced_fuel_a1": 1.03e-4,
            "reduced_fuel_a2": 3.22,
            "reduced_fuel_intercept": 1217,
        },
        "B735": {
            "reduced_fuel_a1": 7.44e-5,
            "reduced_fuel_a2": 2.65,
            "reduced_fuel_intercept": 1185,
        },
        "B736": {
            "reduced_fuel_a1": 5.92e-5,
            "reduced_fuel_a2": 2.40,
            "reduced_fuel_intercept": 1185,
        },
        "B737": {
            "reduced_fuel_a1": 8.39e-5,
            "reduced_fuel_a2": 2.50,
            "reduced_fuel_intercept": 1310,
        },
        "B738": {
            "reduced_fuel_a1": 7.13e-5,
            "reduced_fuel_a2": 2.94,
            "reduced_fuel_intercept": 1275,
        },
        "B739": {
            "reduced_fuel_a1": 5.46e-5,
            "reduced_fuel_a2": 3.11,
            "reduced_fuel_intercept": 1227,
        },
        "B744": {
            "reduced_fuel_a1": 3.49e-4,
            "reduced_fuel_a2": 8.19,
            "reduced_fuel_intercept": 5726,
        },
        "B748": {
            "reduced_fuel_a1": 2.81e-4,
            "reduced_fuel_a2": 6.98,
            "reduced_fuel_intercept": 6855,
        },
        "B752": {
            "reduced_fuel_a1": 1.25e-4,
            "reduced_fuel_a2": 3.66,
            "reduced_fuel_intercept": 1935,
        },
        "B753": {
            "reduced_fuel_a1": 1.39e-4,
            "reduced_fuel_a2": 4.32,
            "reduced_fuel_intercept": 2005,
        },
        "B762": {
            "reduced_fuel_a1": 1.56e-4,
            "reduced_fuel_a2": 4.46,
            "reduced_fuel_intercept": 2198,
        },
        "B763": {
            "reduced_fuel_a1": 1.50e-4,
            "reduced_fuel_a2": 4.19,
            "reduced_fuel_intercept": 3042,
        },
        "B764": {
            "reduced_fuel_a1": 1.44e-4,
            "reduced_fuel_a2": 5.10,
            "reduced_fuel_intercept": 2651,
        },
        "B772": {
            "reduced_fuel_a1": 1.92e-4,
            "reduced_fuel_a2": 5.80,
            "reduced_fuel_intercept": 3886,
        },
        "B773": {
            "reduced_fuel_a1": 5.52e-5,
            "reduced_fuel_a2": 8.82,
            "reduced_fuel_intercept": 1537,
        },
        "B77L": {
            "reduced_fuel_a1": 1.87e-4,
            "reduced_fuel_a2": 5.38,
            "reduced_fuel_intercept": 5189,
        },
        "B77W": {
            "reduced_fuel_a1": 2.25e-4,
            "reduced_fuel_a2": 6.31,
            "reduced_fuel_intercept": 5186,
        },
        "B788": {
            "reduced_fuel_a1": 1.19e-4,
            "reduced_fuel_a2": 3.92,
            "reduced_fuel_intercept": 3125,
        },
        "B789": {
            "reduced_fuel_a1": 1.17e-4,
            "reduced_fuel_a2": 3.91,
            "reduced_fuel_intercept": 3407,
        },
        "B78X": {
            "reduced_fuel_a1": 6.99e-5,
            "reduced_fuel_a2": 4.98,
            "reduced_fuel_intercept": 2821,
        },
        "BCS1": {
            "reduced_fuel_a1": -3.67e-5,
            "reduced_fuel_a2": 2.64,
            "reduced_fuel_intercept": 947,
        },
        "BCS3": {
            "reduced_fuel_a1": 7.22e-5,
            "reduced_fuel_a2": 2.66,
            "reduced_fuel_intercept": 1160,
        },
        "BE20": {
            "reduced_fuel_a1": 1.28e-4,
            "reduced_fuel_a2": 0.41,
            "reduced_fuel_intercept": 96,
        },
        "BE40": {
            "reduced_fuel_a1": 3.59e-4,
            "reduced_fuel_a2": 0.22,
            "reduced_fuel_intercept": 392,
        },
        "BE55": {
            "reduced_fuel_a1": 6.88e-7,
            "reduced_fuel_a2": 0.32,
            "reduced_fuel_intercept": 30,
        },
        "BN2P": {
            "reduced_fuel_a1": -1.01e-8,
            "reduced_fuel_a2": 0.13,
            "reduced_fuel_intercept": 22,
        },
        "C172": {
            "reduced_fuel_a1": 1.24e-6,
            "reduced_fuel_a2": 0.12,
            "reduced_fuel_intercept": 11,
        },
        "C208": {
            "reduced_fuel_a1": -3.30e-5,
            "reduced_fuel_a2": 0.41,
            "reduced_fuel_intercept": 36,
        },
        "C25A": {
            "reduced_fuel_a1": -1.02e-5,
            "reduced_fuel_a2": 0.55,
            "reduced_fuel_intercept": 209,
        },
        "C310": {
            "reduced_fuel_a1": 9.12e-7,
            "reduced_fuel_a2": 0.26,
            "reduced_fuel_intercept": 45,
        },
        "C680": {
            "reduced_fuel_a1": 2.77e-5,
            "reduced_fuel_a2": 0.87,
            "reduced_fuel_intercept": 331,
        },
        "CRJ1": {
            "reduced_fuel_a1": 1.04e-4,
            "reduced_fuel_a2": 1.31,
            "reduced_fuel_intercept": 501,
        },
        "CRJ2": {
            "reduced_fuel_a1": -2.13e-5,
            "reduced_fuel_a2": 1.44,
            "reduced_fuel_intercept": 440,
        },
        "CRJ7": {
            "reduced_fuel_a1": 6.35e-5,
            "reduced_fuel_a2": 1.88,
            "reduced_fuel_intercept": 683,
        },
        "CRJ9": {
            "reduced_fuel_a1": 6.24e-5,
            "reduced_fuel_a2": 1.95,
            "reduced_fuel_intercept": 680,
        },
        "CRJX": {
            "reduced_fuel_a1": 7.56e-5,
            "reduced_fuel_a2": 1.88,
            "reduced_fuel_intercept": 733,
        },
        "CVLT": {
            "reduced_fuel_a1": 1.66e-4,
            "reduced_fuel_a2": 1.16,
            "reduced_fuel_intercept": 189,
        },
        "D228": {
            "reduced_fuel_a1": -5.84e-4,
            "reduced_fuel_a2": 0.94,
            "reduced_fuel_intercept": 3,
        },
        "D328": {
            "reduced_fuel_a1": -2.02e-4,
            "reduced_fuel_a2": 1.02,
            "reduced_fuel_intercept": 111,
        },
        "DC94": {
            "reduced_fuel_a1": -7.59e-4,
            "reduced_fuel_a2": 4.66,
            "reduced_fuel_intercept": 1425,
        },
        "DH8A": {
            "reduced_fuel_a1": 5.56e-5,
            "reduced_fuel_a2": 1.20,
            "reduced_fuel_intercept": 83,
        },
        "DH8B": {
            "reduced_fuel_a1": 5.33e-5,
            "reduced_fuel_a2": 1.13,
            "reduced_fuel_intercept": 130,
        },
        "DH8C": {
            "reduced_fuel_a1": 3.80e-5,
            "reduced_fuel_a2": 1.20,
            "reduced_fuel_intercept": 131,
        },
        "DH8D": {
            "reduced_fuel_a1": 4.20e-5,
            "reduced_fuel_a2": 1.70,
            "reduced_fuel_intercept": 284,
        },
        "DHC2": {
            "reduced_fuel_a1": 6.06e-9,
            "reduced_fuel_a2": 0.14,
            "reduced_fuel_intercept": 19,
        },
        "DHC3": {
            "reduced_fuel_a1": 6.06e-9,
            "reduced_fuel_a2": 0.14,
            "reduced_fuel_intercept": 19,
        },
        "DHC6": {
            "reduced_fuel_a1": -3.19e-5,
            "reduced_fuel_a2": 0.69,
            "reduced_fuel_intercept": 29,
        },
        "DHC7": {
            "reduced_fuel_a1": 2.37e-4,
            "reduced_fuel_a2": 1.10,
            "reduced_fuel_intercept": 178,
        },
        "DOVE": {
            "reduced_fuel_a1": 3.97e-7,
            "reduced_fuel_a2": 0.48,
            "reduced_fuel_intercept": 41,
        },
        "E110": {
            "reduced_fuel_a1": -3.95e-4,
            "reduced_fuel_a2": 0.80,
            "reduced_fuel_intercept": 26,
        },
        "E120": {
            "reduced_fuel_a1": 3.55e-5,
            "reduced_fuel_a2": 0.77,
            "reduced_fuel_intercept": 131,
        },
        "E135": {
            "reduced_fuel_a1": 3.77e-5,
            "reduced_fuel_a2": 1.28,
            "reduced_fuel_intercept": 454,
        },
        "E145": {
            "reduced_fuel_a1": 6.63e-5,
            "reduced_fuel_a2": 1.37,
            "reduced_fuel_intercept": 467,
        },
        "E170": {
            "reduced_fuel_a1": 7.15e-5,
            "reduced_fuel_a2": 1.79,
            "reduced_fuel_intercept": 746,
        },
        "E190": {
            "reduced_fuel_a1": 1.74e-5,
            "reduced_fuel_a2": 2.29,
            "reduced_fuel_intercept": 900,
        },
        "E195": {
            "reduced_fuel_a1": 8.80e-5,
            "reduced_fuel_a2": 2.37,
            "reduced_fuel_intercept": 922,
        },
        "E55P": {
            "reduced_fuel_a1": 2.84e-5,
            "reduced_fuel_a2": 0.50,
            "reduced_fuel_intercept": 263,
        },
        "E75L": {
            "reduced_fuel_a1": 6.13e-5,
            "reduced_fuel_a2": 1.75,
            "reduced_fuel_intercept": 772,
        },
        "E75S": {
            "reduced_fuel_a1": 7.62e-5,
            "reduced_fuel_a2": 1.87,
            "reduced_fuel_intercept": 759,
        },
        "F100": {
            "reduced_fuel_a1": 2.57e-5,
            "reduced_fuel_a2": 2.55,
            "reduced_fuel_intercept": 987,
        },
        "F27": {
            "reduced_fuel_a1": -2.55e-4,
            "reduced_fuel_a2": 1.73,
            "reduced_fuel_intercept": 197,
        },
        "F28": {
            "reduced_fuel_a1": -2.13e-4,
            "reduced_fuel_a2": 2.44,
            "reduced_fuel_intercept": 919,
        },
        "F406": {
            "reduced_fuel_a1": -1.51e-4,
            "reduced_fuel_a2": 0.58,
            "reduced_fuel_intercept": 39,
        },
        "F50": {
            "reduced_fuel_a1": -1.67e-5,
            "reduced_fuel_a2": 1.60,
            "reduced_fuel_intercept": 98,
        },
        "F70": {
            "reduced_fuel_a1": 4.87e-5,
            "reduced_fuel_a2": 2.11,
            "reduced_fuel_intercept": 883,
        },
        "GLF4": {
            "reduced_fuel_a1": -8.48e-6,
            "reduced_fuel_a2": 2.00,
            "reduced_fuel_intercept": 776,
        },
        "GLF5": {
            "reduced_fuel_a1": 9.22e-5,
            "reduced_fuel_a2": 1.08,
            "reduced_fuel_intercept": 861,
        },
        "IL96": {
            "reduced_fuel_a1": 3.35e-4,
            "reduced_fuel_a2": 6.67,
            "reduced_fuel_intercept": 3893,
        },
        "J328": {
            "reduced_fuel_a1": 2.31e-4,
            "reduced_fuel_a2": 0.97,
            "reduced_fuel_intercept": 519,
        },
        "JS31": {
            "reduced_fuel_a1": -6.63e-7,
            "reduced_fuel_a2": 0.57,
            "reduced_fuel_intercept": 67,
        },
        "JS32": {
            "reduced_fuel_a1": -3.19e-5,
            "reduced_fuel_a2": 0.63,
            "reduced_fuel_intercept": 60,
        },
        "JS41": {
            "reduced_fuel_a1": -8.91e-6,
            "reduced_fuel_a2": 0.77,
            "reduced_fuel_intercept": 105,
        },
        "L410": {
            "reduced_fuel_a1": -2.64e-5,
            "reduced_fuel_a2": 0.89,
            "reduced_fuel_intercept": 54,
        },
        "MD81": {
            "reduced_fuel_a1": 2.26e-4,
            "reduced_fuel_a2": 3.28,
            "reduced_fuel_intercept": 1467,
        },
        "MD82": {
            "reduced_fuel_a1": 1.68e-4,
            "reduced_fuel_a2": 3.31,
            "reduced_fuel_intercept": 1425,
        },
        "MD83": {
            "reduced_fuel_a1": 1.55e-4,
            "reduced_fuel_a2": 3.41,
            "reduced_fuel_intercept": 1402,
        },
        "MD87": {
            "reduced_fuel_a1": 1.30e-4,
            "reduced_fuel_a2": 3.13,
            "reduced_fuel_intercept": 1391,
        },
        "MD88": {
            "reduced_fuel_a1": 1.69e-4,
            "reduced_fuel_a2": 3.30,
            "reduced_fuel_intercept": 1430,
        },
        "MD90": {
            "reduced_fuel_a1": 1.65e-4,
            "reduced_fuel_a2": 3.41,
            "reduced_fuel_intercept": 1413,
        },
        "P28B": {
            "reduced_fuel_a1": 2.44e-7,
            "reduced_fuel_a2": 0.14,
            "reduced_fuel_intercept": 18,
        },
        "PA31": {
            "reduced_fuel_a1": 3.94e-7,
            "reduced_fuel_a2": 0.48,
            "reduced_fuel_intercept": 41,
        },
        "PA46": {
            "reduced_fuel_a1": -1.67e-4,
            "reduced_fuel_a2": 0.29,
            "reduced_fuel_intercept": 18,
        },
        "PC12": {
            "reduced_fuel_a1": 3.00e-5,
            "reduced_fuel_a2": 0.30,
            "reduced_fuel_intercept": 55,
        },
        "RJ1H": {
            "reduced_fuel_a1": 2.38e-4,
            "reduced_fuel_a2": 2.57,
            "reduced_fuel_intercept": 1243,
        },
        "RJ85": {
            "reduced_fuel_a1": 1.22e-4,
            "reduced_fuel_a2": 2.51,
            "reduced_fuel_intercept": 1148,
        },
        "SB20": {
            "reduced_fuel_a1": 7.04e-5,
            "reduced_fuel_a2": 1.23,
            "reduced_fuel_intercept": 241,
        },
        "SF34": {
            "reduced_fuel_a1": 3.93e-5,
            "reduced_fuel_a2": 0.86,
            "reduced_fuel_intercept": 106,
        },
        "SU95": {
            "reduced_fuel_a1": -1.78e-5,
            "reduced_fuel_a2": 2.62,
            "reduced_fuel_intercept": 784,
        },
        "SW4": {
            "reduced_fuel_a1": 3.89e-5,
            "reduced_fuel_a2": 0.54,
            "reduced_fuel_intercept": 80,
        },
        "T134": {
            "reduced_fuel_a1": 1.65e-4,
            "reduced_fuel_a2": 2.27,
            "reduced_fuel_intercept": 1924,
        },
        "T154": {
            "reduced_fuel_a1": -3.58e-5,
            "reduced_fuel_a2": 6.32,
            "reduced_fuel_intercept": 1827,
        },
        "T204": {
            "reduced_fuel_a1": 1.51e-4,
            "reduced_fuel_a2": 3.77,
            "reduced_fuel_intercept": 1797,
        },
        "Y12": {
            "reduced_fuel_a1": 8.31e-6,
            "reduced_fuel_a2": 0.47,
            "reduced_fuel_intercept": 38,
        },
        "YK40": {
            "reduced_fuel_a1": -1.81e-4,
            "reduced_fuel_a2": 2.52,
            "reduced_fuel_intercept": 494,
        },
        "YK42": {
            "reduced_fuel_a1": -3.78e-5,
            "reduced_fuel_a2": 4.27,
            "reduced_fuel_intercept": 1164,
        },
    }

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(seymour_etal._regression_coefficients.keys())

    @staticmethod
    @ureg.check(
        None,
        "[length]",
    )
    def calculate(
        acft: str,
        R: pint.Quantity,
    ) -> pint.Quantity:
        """
        Given an ICAO aircraft designator and the great-circle distance, calculates the fuel burned.

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator
        R : pint.Quantity
            Great-circle distance between origin and destination [length]

        Returns
        -------
        pint.Quantity
            Fuel mass [kg]

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        ValueError
            If the great-circle distance is negative.
        ValueError
            If the fit returns no positive fuel burn at this distance
            (types with a negative $a_1$, far beyond their maximum range).

        Warnings
        --------
        An "average" payload is assumed for every aircraft. Distance is the only variable.
        """
        if acft not in seymour_etal._regression_coefficients.keys():
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )
        if R < 0:
            raise ValueError("Great-circle distance must be non-negative.")

        R = R.to("km").magnitude

        m_f = (
            seymour_etal._regression_coefficients[acft]["reduced_fuel_a1"] * R**2
            + seymour_etal._regression_coefficients[acft]["reduced_fuel_a2"] * R
            + seymour_etal._regression_coefficients[acft]["reduced_fuel_intercept"]
        )
        # Types with a negative a1 bend downward far beyond their fitted range.
        if m_f <= 0:
            raise ValueError(
                f"The fit for '{acft}' returns no positive fuel burn at {R:.0f} km, "
                "which lies outside its fitted range."
            )
        return m_f * ureg("kg")


class aim2015:
    r"""
    Reduced-order fuel burn model based on Dray et al. (2019).

    The class implements the reduced-order fuel burn model of the [AIM2015 air transport model](https://www.atslab.org/data-tools/) (part "Aircraft Performance Model"):

    ![AIM2015 Visual Abstract](../_static/reduced_order_aim2015.svg)

    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    by simulating flights using the [PianoX software](https://www.lissys.uk/PianoX.html).

    Fuel burn is calculated according to Section 3.4.1 of the AIM2015 documentation:

    $$
        \text{Fuel}_{tsp} = I_{ts} \cdot ( \eta_{tsp,0} + \eta_{tsp,1}D + \eta_{tsp,2}D \cdot PL + \eta_{tsp,3}D^2 + \eta_{tsp,4}PL + \eta_{tsp,5}D^2 \cdot PL )
    $$

    where subscripts $t,s,p$ denote aircraft $t$ype, $s$ize class and flight $p$hase and where:

    | Symbol     | Dimension         | Description                                                            |
    |------------|-------------------|------------------------------------------------------------------------|
    | $I$        | [dimensionless]   | non-linear inefficiency parameter                                      |
    | $D$        | [length]          | distance flown in flight phase                                         |
    | $PL$       | [mass]            | payload mass                                                           |
    | $\eta$     | varies            | regression coefficients                                                |

    For information on the inefficiency parameter $I$, see the conference publication of Reynolds (2009).

    Warnings
    --------
    While the AIM2015 documentation lists the Boeing 777-300ER using the PW4090 engine,
    this aircraft variant [was exclusively powered by GE90 engines](https://en.wikipedia.org/wiki/Boeing_777#Engines).

    See Also
    --------
    Class `AircraftPerformanceParams` in `aim/v11/datastructures/AircraftPerformanceParams`

    Notes
    -----
    Data is available for 8 aircraft size classes, as defined in the AIM2015 documentation, Section 2.3, Table 1:

    | Index | Size Category         | PAX Number    | Reference Aircraft | Reference Engine     |
    |-------|-----------------------|---------------|--------------------|----------------------|
    | 1     | Small Regional Jet    | 30-69         | CRJ 700            | GE CF34 8C5B1        |
    | 2     | Large Regional Jet    | 70-109        | Embraer 190        | GE CF34 10E6         |
    | 3     | Small Narrowbody      | 110-129       | Airbus A319        | V.2522               |
    | 4     | Medium Narrowbody     | 130-159       | Airbus A320        | CFM56-5B4            |
    | 5     | Large Narrowbody      | 160-199       | Boeing 737-800     | CFM56-7B27           |
    | 6     | Small Twin Aisle      | 200-249       | Boeing 787-800     | GEnx-1B67            |
    | 7     | Medium Twin Aisle     | 259-299       | Airbus A330-300    | Trent 772B           |
    | 8     | Large Twin Aisle      | 300-399       | Boeing 777-300ER   | PW4090               |

    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                  |
    |-----------------------|-----------------------------------------------------------------------------|
    | data availability     | 8 selected aircraft, which can be used as proxies within their weight class |
    | aircraft payload      | variable                                                                    |
    | climb/descent         | considered separately                                                       |
    | reserve fuel uplift   | considered implicitly (?)                                                   |
    | diversion fuel uplift | considered implicitly (?)                                                   |

    References
    ----------
    - Dray, L. M., Krammer, P., Doyme, K., Wang, B., Al Zayat, K., O'Sullivan, A., & Schäfer, A. W. (2019).
    AIM2015: Validation and initial results from an open-source aviation systems model.
    _Transport Policy_, 79, 93-102.
    doi:[10.1016/j.tranpol.2019.04.013](https://doi.org/10.1016/j.tranpol.2019.04.013)
    - Reynolds, T. G. (2009).
    Development of flight inefficiency metrics for environmental performance assessment of ATM.
    In _8th USA/Europe Seminar on Air Traffic Management Research and Development (ATM2009)_.
    Full Text: [Archived Copy from atslab.org](https://web.archive.org/web/20220721111106/http://www.atslab.org/wp-content/uploads/2017/01/ATM2009_Reynoldsv2.pdf)
    - [AIM2015 documentation (v9)](https://web.archive.org/web/20241206191807/https://www.atslab.org/wp-content/uploads/2019/12/AIM-2015-Documentation-v9-122019.pdf)
    - [AIM2015 documentation (v11)](https://web.archive.org/web/20231001131622/https://www.atslab.org/wp-content/uploads/2023/02/AIM-2015-Documentation-v11.pdf)
    - [AIM2015 information in the EU MIDAS system](https://web.jrc.ec.europa.eu/policy-model-inventory/explore/models/model-aim/)

    Licensing Note
    --------------
    Parameters from `AircraftPerformanceParams.csv` of AIM2015 v11
    (UCL Air Transportation Systems Laboratory), MIT License.
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import aim2015
    aim2015.calculate(
        acft_size_class=8,
        D_climb=300*ureg.km,
        D_cruise=(15000-300-200)*ureg.km,
        D_descent=200*ureg.km,
        PL=55.5*ureg.metric_ton
    )
    ```
    """

    _regression_coefficients = {}
    with resources.open_text(
        "jetfuelburn.data.AIM2015", "AIM2015_v11_AircraftPerformanceParams.csv"
    ) as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            variable = row.pop("Variable")
            _regression_coefficients[variable] = {
                key: float(value) for key, value in row.items()
            }

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(["CRJ7", "E190", "A319", "A320", "B738", "B788", "A333", "B77W"])

    @staticmethod
    @ureg.check(
        None,
        "[length]",
        "[length]",
        "[length]",
        "[mass]",
    )
    def calculate(
        acft_size_class: int,
        D_climb: pint.Quantity,
        D_cruise: pint.Quantity,
        D_descent: pint.Quantity,
        PL: pint.Quantity,
    ) -> dict[str, pint.Quantity]:
        """
        Given an aircraft size class integer, payload and distances for climb, cruise, and descent, calculates the fuel burned during flight.

        Parameters
        ----------
        acft_size_class : int
            Aircraft size class (1-8)
        D_climb : pint.Quantity
            Climb distance [length]
        D_cruise : pint.Quantity
            Cruise distance [length]
        D_descent : pint.Quantity
            Descent distance [length]
        PL : pint.Quantity
            Payload [mass]

        Returns
        -------
        dict[str, pint.Quantity]
            'mass_fuel_climb' : pint.Quantity
                Fuel mass (climb segment) [kg]
            'mass_fuel_cruise' : pint.Quantity
                Fuel mass (cruise segment) [kg]
            'mass_fuel_descent' : pint.Quantity
                Fuel mass (descent segment) [kg]

        Raises
        ------
        ValueError
            If range or payload is negative, or if the aircraft size class is not between 1 and 8.
        """
        if D_climb.magnitude < 0:
            raise ValueError("Climb distance must be non-negative.")
        if D_cruise.magnitude < 0:
            raise ValueError("Cruise distance must be non-negative.")
        if D_descent.magnitude < 0:
            raise ValueError("Descent distance must be non-negative.")
        if PL.magnitude < 0:
            raise ValueError("Payload must be non-negative.")
        if acft_size_class not in range(1, 9):
            raise ValueError(
                "Aircraft size class must be between 1 and 8. Compare the table in the class documentation."
            )

        D_climb = D_climb.to("km").magnitude
        D_cruise = D_cruise.to("km").magnitude
        D_descent = D_descent.to("km").magnitude
        PL = PL.to("kg").magnitude

        m_f_climb = (
            aim2015._regression_coefficients["ClimboutFuel_kg_Intercept"][
                f"Param_Size{acft_size_class}"
            ]
            + aim2015._regression_coefficients["ClimboutFuel_kg_Dist_km"][
                f"Param_Size{acft_size_class}"
            ]
            * D_climb
            + aim2015._regression_coefficients["ClimboutFuel_kg_Dist_km_x_Payload_kg"][
                f"Param_Size{acft_size_class}"
            ]
            * D_climb
            * PL
            + aim2015._regression_coefficients["ClimboutFuel_kg_Dist_km_squared"][
                f"Param_Size{acft_size_class}"
            ]
            * D_climb**2
            + aim2015._regression_coefficients["ClimboutFuel_kg_Payload_kg"][
                f"Param_Size{acft_size_class}"
            ]
            * PL
            + aim2015._regression_coefficients[
                "ClimboutFuel_kg_Dist_km_squared_x_Payload_kg"
            ][f"Param_Size{acft_size_class}"]
            * D_climb**2
            * PL
        )
        m_f_cruise = (
            aim2015._regression_coefficients["CruiseFuel_kg_Intercept"][
                f"Param_Size{acft_size_class}"
            ]
            + aim2015._regression_coefficients["CruiseFuel_kg_Dist_km"][
                f"Param_Size{acft_size_class}"
            ]
            * D_cruise
            + aim2015._regression_coefficients["CruiseFuel_kg_Dist_km_x_Payload_kg"][
                f"Param_Size{acft_size_class}"
            ]
            * D_cruise
            * PL
            + aim2015._regression_coefficients["CruiseFuel_kg_Dist_km_squared"][
                f"Param_Size{acft_size_class}"
            ]
            * D_cruise**2
            + aim2015._regression_coefficients["CruiseFuel_kg_Payload_kg"][
                f"Param_Size{acft_size_class}"
            ]
            * PL
            + aim2015._regression_coefficients[
                "CruiseFuel_kg_Dist_km_squared_x_Payload_kg"
            ][f"Param_Size{acft_size_class}"]
            * D_cruise**2
            * PL
        )
        m_f_descent = (
            aim2015._regression_coefficients["DescentFuel_kg_Intercept"][
                f"Param_Size{acft_size_class}"
            ]
            + aim2015._regression_coefficients["DescentFuel_kg_Dist_km"][
                f"Param_Size{acft_size_class}"
            ]
            * D_descent
            + aim2015._regression_coefficients["DescentFuel_kg_Dist_km_x_Payload_kg"][
                f"Param_Size{acft_size_class}"
            ]
            * D_descent
            * PL
            + aim2015._regression_coefficients["DescentFuel_kg_Dist_km_squared"][
                f"Param_Size{acft_size_class}"
            ]
            * D_descent**2
            + aim2015._regression_coefficients["DescentFuel_kg_Payload_kg"][
                f"Param_Size{acft_size_class}"
            ]
            * PL
            + aim2015._regression_coefficients[
                "DescentFuel_kg_Dist_km_squared_x_Payload_kg"
            ][f"Param_Size{acft_size_class}"]
            * D_descent**2
            * PL
        )

        return {
            "mass_fuel_climb": m_f_climb * ureg("kg"),
            "mass_fuel_cruise": m_f_cruise * ureg("kg"),
            "mass_fuel_descent": m_f_descent * ureg("kg"),
        }


class eea_emission_inventory_2009:
    r"""
    The class implements the reduced-order fuel burn model of the [EMEP/EEA air pollutant emission inventory guidebook](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023) (2009).

    ![EEA 2009 Visual Abstract](../_static/reduced_order_eea2009.svg)

    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    by simulating flights using the [PianoX software](https://www.lissys.uk/PianoX.html).

    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                  |
    |-----------------------|-----------------------------------------------------------------------------|
    | data availability     | 19 selected aircraft                                                        |
    | aircraft payload      | fixed, unclear                                                              |
    | climb/descent         | not considered separately                                                   |
    | reserve fuel uplift   | considered implicitly (?)                                                   |
    | diversion fuel uplift | considered implicitly (?)                                                   |

    Warnings
    --------
    Note that only EEA data between 1999-2009 was based on Piano simulations, as documented in the `Aviation_annex.zip` file.
    Later versions of the EEA guidebook (2013, 2016, 2019, 2023) instead use the Eurocontrol Advanced Emission Model (AEM), as documented in the respective guidebook files.
    These later models could not be incorporated into `jetfuelburn` for licensing reasons.

    Notes
    -----
    Data on military and transport aircraft from the sub-table `1.A.3.a Aviation vs2.3spreadsheet2-1updated2007.xlsx`
    [used with permission](../_static/permissions/email_foi_se.pdf)
    by the Swedish Defence Research Agency (foi.se). Note that this data may be a poor representation of
    newer variants of the same aircraft types.

    References
    ----------
    - [EMEP/EEA air pollutant emission inventory guidebook - 2009, Part B, Section 1 (Energy), Subsection 1.A.3.a (`Aviation_annex.zip`)](https://www.eea.europa.eu/en/analysis/publications/emep-eea-emission-inventory-guidebook-2009)

    Licensing Note
    --------------
    Jet aircraft data from the EMEP/EEA air pollutant emission inventory guidebook 2009, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
    Turboprop and military transport data from FOI (Swedish Defence Research Agency), used with permission.
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import eea_emission_inventory_2009
    eea_emission_inventory_2009.calculate(
        acft='A320',
        R=1500*ureg.km
    )
    ```
    """

    _aircraft_data = {}
    with resources.open_text("jetfuelburn.data.EEA2009", "data.json") as file:
        _aircraft_data = json.load(file)

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(eea_emission_inventory_2009._aircraft_data.keys())

    @staticmethod
    @ureg.check(
        None,
        "[length]",
    )
    def calculate(
        acft: str,
        R: pint.Quantity,
    ) -> dict[str, pint.Quantity]:
        r"""
        Given an aircraft name and range, calculates the fuel burned during flight.

        Data between reported range/fuel-burn points is interpolated linearly:

        $$
            m_F(R=200) = m_F(125) + (200-125) \cdot \frac{m_F(250) - m_F(125)}{250 - 125}
        $$

        where in this example, data is available for $R=[125,250]$ miles and a user-defined range of $R=200$ miles is requested.

        | Symbol     | Dimension         | Description                                                            |
        |------------|-------------------|------------------------------------------------------------------------|
        | $m_F$      | [mass]            | fuel mass burned during flight                                         |
        | $R$        | [length]          | mission range                                                          |

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator. Some entries stand for an aircraft family (e.g. `A330`, `B757`, `B777`),
            because the guidebook reports one representative type per family (see `list_aircraft()`).
        R : pint.Quantity
            Mission range [length]

        Returns
        -------
        dict[str, pint.Quantity]
            'mass_fuel_total' : pint.Quantity
                Fuel mass (total segment) [kg]
            'mass_fuel_LTO' : pint.Quantity
                Fuel mass (LTO segment) [kg]
            'mass_fuel_taxi_in' : pint.Quantity
                Fuel mass (taxi-in segment) [kg]
            'mass_fuel_climbout' : pint.Quantity
                Fuel mass (climbout segment) [kg]
            'mass_fuel_takeoff' : pint.Quantity
                Fuel mass (takeoff segment) [kg]
            'mass_fuel_climb_cruise_descent' : pint.Quantity
                Fuel mass (climb, cruise, and descent segments) [kg]
            'mass_fuel_approach_landing' : pint.Quantity
                Fuel mass (approach and landing segment) [kg]
            'mass_fuel_taxi_out' : pint.Quantity
                Fuel mass (taxi-out segment) [kg]

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        ValueError
            If the range is negative or the range is outside the available data range for the given aircraft.
        """

        R = R.to("nmi").magnitude

        if acft not in eea_emission_inventory_2009._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )
        else:
            aircraft_data = eea_emission_inventory_2009._aircraft_data[acft]
            list_distance_points = sorted(
                [int(k) for k in aircraft_data["total"].keys()]
            )

        if R < list_distance_points[0]:
            raise ValueError(f"Range must be at least {list_distance_points[0]} nmi.")
        if R > list_distance_points[-1]:
            raise ValueError(f"Range must be at most {list_distance_points[-1]} nmi.")

        list_flight_phases = [
            "total",
            "LTO",
            "taxi_in",
            "climbout",
            "takeoff",
            "climb_cruise_descent",
            "approach_landing",
            "taxi_out",
        ]

        dict_fuel_burn = {}
        for flight_phase in list_flight_phases:
            dict_fuel_burn_per_distance = {
                int(key): value for key, value in aircraft_data[flight_phase].items()
            }

            for index_distance_point in range(len(list_distance_points) - 1):
                if (
                    list_distance_points[index_distance_point]
                    <= R
                    < list_distance_points[index_distance_point + 1]
                ):
                    x1, x2 = (
                        list_distance_points[index_distance_point],
                        list_distance_points[index_distance_point + 1],
                    )
                    y1, y2 = (
                        dict_fuel_burn_per_distance[x1],
                        dict_fuel_burn_per_distance[x2],
                    )
                    dict_fuel_burn[flight_phase] = y1 + (R - x1) * (y2 - y1) / (x2 - x1)
                    break
            # If R equals the last key value
            if R == list_distance_points[-1]:
                dict_fuel_burn[flight_phase] = dict_fuel_burn_per_distance[
                    list_distance_points[-1]
                ]

        dict_fuel_burn_result = {}
        for key, value in dict_fuel_burn.items():
            dict_fuel_burn_result[f"mass_fuel_{key}"] = value * ureg("kg")

        return dict_fuel_burn_result


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
    | $x$        | [distance]        | Flight distance in km: great-circle distance plus 95 km detour         |
    | $a$        | [mass/distance²]  | Coefficient of the quadratic term                                      |
    | $b$        | [mass/distance]   | Coefficient of the linear term                                         |
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

    The coefficients $a$, $b$ and $c$ are those of the two parameter tables in section 11 ("Formula")
    of the Calculation Principles page: standard short-haul flight, Boeing 737 and A320 in the first table,
    standard long-haul flight, Boeing 777 and A330 in the second.

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

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import myclimate
    myclimate.list_aircraft()[0:10]
    myclimate.calculate(
        acft='B737',
        x=2200*ureg.km,
    )
    ```
    """

    _regression_coefficients = {
        "A320": {"a": 0.000032, "b": 2.588, "c": 1212.084},
        "B737": {"a": 0.00016, "b": 1.454, "c": 1531.722},
        "A330": {"a": 0.00034, "b": 4.384, "c": 2457.737},
        "B777": {"a": 0.00034, "b": 6.112, "c": 3403.041},
        "standard aircraft": {},
    }

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(myclimate._regression_coefficients.keys())

    @staticmethod
    @ureg.check(
        None,  # acft
        "[length]",
    )
    def calculate(
        acft: str,
        x: pint.Quantity,
    ) -> pint.Quantity:
        r"""
        Given a flight distance, calculate the fleet-average fuel consumption of a flight using the
        [myClimate Flight Emissions Calculator](https://co2.myclimate.org/en/flight_calculators/new).

        Parameters
        ----------
        acft : str
            Aircraft type: `A320`, `B737`, `A330`, `B777` or `standard aircraft` (see `list_aircraft()`)
        x : pint.Quantity
            Flight distance [length]. myclimate defines it as the great-circle distance
            plus a detour correction of 95 km.

        Returns
        -------
        pint.Quantity
            Fuel mass [kg]

        Warnings
        --------
        It is not entirely clear from the description of the myClimate Flight Emissions Calculator
        how distances of <1500km for short-haul aircraft and distances of >2500km for long-haul aircraft
        are handled. [The description](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/) mentions that

        > "The fuel consumption for distances between 1500 and 2500 km is linearly interpolated."

        but this would make sense only for the "standard short-haul" and "standard long-haul" aircraft?

        In this function, the short-haul aircraft (A320, B737) therefore accept distances up to 2500 km
        and the long-haul aircraft (A330, B777) distances from 1500 km. The `standard aircraft` option
        can be used for all distances.
        """
        if x < (0 * ureg.km):
            raise ValueError("Distance must not be negative.")
        x = x.to("km").magnitude

        if acft in ["A320", "B737"] and x > 2500:
            raise ValueError(f"Aircraft {acft} is not valid for distances > 2500 km.")
        if acft in ["A330", "B777"] and x < 1500:
            raise ValueError(f"Aircraft {acft} is not valid for distances < 1500 km.")

        if acft == "standard aircraft":
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
            a = myclimate._regression_coefficients[acft]["a"]
            b = myclimate._regression_coefficients[acft]["b"]
            c = myclimate._regression_coefficients[acft]["c"]

        return (a * x**2 + b * x + c) * ureg.kg


class gossling_etal:
    r"""
    This class implements the reduced-order fuel burn model of Gössling, Humpe & Leitão (2024):

    In this model, fuel burn is calculated from a single model-specific hourly fuel consumption value.
    The hourly fuel consumption values were compiled manually from public manufacturer/broker brochures
    of aircraft marketed as business or private jets, and paired with flight times derived from
    [ADS-B Exchange](https://globe.adsbexchange.com) tracking data.

    Fuel burn is calculated according to the function `leg_co2_kg()` in
    [the code supplement](https://github.com/jorgecardleitao/private-jets/blob/main/src/emissions.rs)
    to Gössling, Humpe & Leitão (2024):

    $$
        m_{fuel} = FF \cdot t \cdot \gamma \cdot \rho
    $$

    with the associated CO2 emissions given by:

    $$
        m_{CO_2} = m_{fuel} \cdot \epsilon
    $$

    where:

    | Symbol         | Dimension                | Description                                                       |
    |----------------|--------------------------|-------------------------------------------------------------------|
    | $m_{fuel}$     | [mass]                   | Fuel burned during the flight                                     |
    | $m_{CO_2}$     | [mass]                   | CO2 emitted during the flight                                     |
    | $FF$           | [volume] / [time]        | Model-specific hourly fuel consumption (gallons per hour)         |
    | $t$            | [time]                   | Flight time                                                       |
    | $\gamma$       | [dimensionless]          | Volume of one US gallon in litres ($3.78541 \, \text{L/gal}$)     |
    | $\rho$         | [mass] / [volume]        | Density of Jet-A fuel ($0.8 \, \text{kg/L}$)                      |
    | $\epsilon$     | [dimensionless]          | CO2 emitted per unit mass of Jet-A burned ($3.16$)                |

    The hourly fuel consumption $FF$ of a given model is the average over all tabulated sources for that model,
    computed with integer (truncating) division as in the reference implementation
    (cf. `load_private_jet_models()` in [`src/model.rs`](https://github.com/jorgecardleitao/private-jets/blob/main/src/model.rs)).

    Warnings
    --------
    The hourly fuel consumption values are figures from manufacturer/broker brochures ("marketing material"),
    not operational data. The authors estimate the associated uncertainty at a standard deviation of at most 10%,
    and note that, because a single constant fuel flow is applied irrespective of flight phase, distance, altitude,
    payload or load factor, the resulting emission estimates "likely represent a lower boundary estimate".

    See Also
    --------
    - Methodology `M-models-for-private-use` in the [Private Jets methodology](https://github.com/jorgecardleitao/private-jets/blob/main/methodology.md)
    - Fuel/CO2 conversion `leg_co2_kg()` in [`src/emissions.rs`](https://github.com/jorgecardleitao/private-jets/blob/main/src/emissions.rs)
    - Per-model averaging `load_private_jet_models()` in [`src/model.rs`](https://github.com/jorgecardleitao/private-jets/blob/main/src/model.rs)

    Notes
    -----
    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                       |
    |-----------------------|----------------------------------------------------------------------------------|
    | data availability     | 69 business/private-jet types (75 models in the dataset, 72 in the paper)        |
    | aircraft payload      | not considered (a single hourly fuel flow is used per model)                     |
    | climb/descent         | folded into a single model-average hourly fuel flow                              |
    | reserve fuel uplift   | not considered                                                                   |
    | diversion fuel uplift | not considered                                                                   |

    References
    ----------
    Gössling, S., Humpe, A., & Leitão, J. (2024).
    Private aviation is making a growing contribution to climate change.
    _Communications Earth & Environment_, 5, 666.
    doi:[10.1038/s43247-024-01775-z](https://doi.org/10.1038/s43247-024-01775-z)

    Licensing Note
    --------------
    Fuel consumption data from `models.csv` of the private-jets repository by Jorge Leitão, MIT License.
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import gossling_etal
    gossling_etal.list_aircraft()[0:10]
    gossling_etal.calculate(
        acft='GLF5',
        flight_time=2*ureg.hour,
    )
    ```
    """

    _LITER_PER_US_GALLON = 3.78541  # litres per US gallon
    _KG_PER_LITER = 0.8  # density of Jet-A fuel [kg/liter]

    _fuel_flow_gph = {}
    with resources.open_text("jetfuelburn.data.Gossling2024", "models.csv") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            model_name = row["model"]
            gph = int(row["gph"])
            if model_name in _fuel_flow_gph:
                _fuel_flow_gph[model_name][0] += gph
                _fuel_flow_gph[model_name][1] += 1
            else:
                _fuel_flow_gph[model_name] = [gph, 1]
    # Average over all tabulated sources per model, replicating the integer (truncating)
    # division of `load_private_jet_models()` in `src/model.rs` of the reference implementation.
    _fuel_flow_gph = {
        model_name: total // count
        for model_name, (total, count) in _fuel_flow_gph.items()
    }
    # Key the models by ICAO aircraft type designator (`icao.csv`). Models that share a designator
    # are averaged. Models without a designator are left out.
    _models_by_icao = {}
    with resources.open_text("jetfuelburn.data.Gossling2024", "icao.csv") as file:
        for row in csv.DictReader(file):
            if row["icao"]:
                _models_by_icao.setdefault(row["icao"], []).append(row["model"])
    _gph_by_model = _fuel_flow_gph
    _fuel_flow_gph = {}
    for icao, models in _models_by_icao.items():
        total = 0
        for model_name in models:
            total += _gph_by_model[model_name]
        _fuel_flow_gph[icao] = total // len(models)

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(gossling_etal._fuel_flow_gph.keys())

    @staticmethod
    @ureg.check(
        None,  # acft
        "[time]",
    )
    def calculate(
        acft: str,
        flight_time: pint.Quantity,
    ) -> pint.Quantity:
        """
        Given an ICAO aircraft designator and a flight time, calculates the fuel burned.

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (see `list_aircraft()`)
        flight_time : pint.Quantity
            Flight time [time]

        Returns
        -------
        pint.Quantity
            Fuel mass [kg]

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        ValueError
            If the flight time is negative.

        Warnings
        --------
        A single, constant model-average hourly fuel consumption is assumed. Flight time is the only variable.
        The associated CO2 emissions can be obtained by multiplying the returned fuel mass by 3.16
        (kg CO2 per kg of Jet-A burned).
        """
        if acft not in gossling_etal._fuel_flow_gph:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )
        if flight_time < 0 * ureg.hour:
            raise ValueError("Flight time must be non-negative.")

        hours = flight_time.to("hour").magnitude
        gph = gossling_etal._fuel_flow_gph[acft]

        m_f = (
            gph
            * hours
            * gossling_etal._LITER_PER_US_GALLON
            * gossling_etal._KG_PER_LITER
        )
        return m_f * ureg("kg")


class turgut_etal:
    r"""
    This class implements the reduced-order cruise fuel-flow model of Turgut et al. (2014):

    In this model, the cruise-phase fuel flow is calculated from a multiple linear regression
    on three flight parameters: cruise altitude, aircraft mass, and true airspeed (TAS).
    The regression coefficients were obtained by fitting these parameters to 4320 cruise observations
    from 3857 domestic flights operated by Turkish Airlines in January 2011 (using flight data records),
    for the Airbus A319/A320/A321 and Boeing 737-700/737-800 aircraft.

    Unlike the block-fuel models in this module, this model returns an instantaneous cruise fuel-flow
    _rate_ (in kg/h) rather than a total mission fuel mass.

    Fuel flow is calculated according to the regression coefficients in Table 2 of Turgut et al. (2014):

    $$
        FF = C_0 + C_h \cdot h + C_m \cdot m + C_V \cdot V
    $$

    where:

    | Symbol     | Dimension                        | Description                                       |
    |------------|----------------------------------|---------------------------------------------------|
    | $FF$       | [mass] / [time]                  | Cruise fuel-flow rate                             |
    | $h$        | [length]                         | Cruise altitude                                   |
    | $m$        | [mass]                           | Aircraft mass                                     |
    | $V$        | [speed]                          | True airspeed (TAS)                               |
    | $C_0$      | [mass] / [time]                  | Regression constant (intercept)                   |
    | $C_h$      | [mass] / ([time] $\cdot$ [length]) | Altitude coefficient                            |
    | $C_m$      | [mass] / ([time] $\cdot$ [mass]) | Mass coefficient                                  |
    | $C_V$      | [mass] / ([time] $\cdot$ [speed]) | TAS coefficient                                  |

    The coefficients are those fitted for the variables in the units of the paper
    (altitude in ft, mass in tonne, TAS in knot, fuel flow in kg/h). Inputs in any other
    units are converted internally.

    Warnings
    --------
    This model returns a cruise fuel-flow **rate** (kg/h), not a total mission fuel mass.
    To obtain the fuel burned in cruise, multiply the returned rate by the cruise time.

    The regression is valid only within the domain of the data it was fitted to:
    cruise altitude of approximately 22,000–40,000 ft, aircraft mass of approximately 45–79 tonne,
    and TAS of approximately 300–440 knot. Extrapolating the linear model far outside these ranges is unreliable.

    See Also
    --------
    Table 2 ("The results of the regression analyses, where the FF parameter is dependent variable")
    in Turgut et al. (2014).

    Notes
    -----
    Regression models available (cf. Table 2 in Turgut et al. (2014)):

    | Key       | Regression model              | $N$    | Adj. $R^2$ |
    |-----------|-------------------------------|--------|------------|
    | `A319`    | Airbus A319                   | 217    | 0.857      |
    | `A320`    | Airbus A320                   | 1200   | 0.828      |
    | `A321`    | Airbus A321                   | 664    | 0.865      |
    | `B737`    | Boeing 737-700                | 213    | 0.913      |
    | `B738`    | Boeing 737-800                | 1643   | 0.882      |
    | `Airbus`  | all Airbus aircraft (Group A) | 2081   | 0.931      |
    | `Boeing`  | all Boeing aircraft (Group B) | 1856   | 0.896      |
    | `Overall` | all aircraft                  | 3937   | 0.924      |

    Key assumptions of this fuel calculation function:

    | Parameter             | Assumption                                                                  |
    |-----------------------|-----------------------------------------------------------------------------|
    | data availability     | 5 narrow-body aircraft, plus 3 grouped models                               |
    | flight phase          | cruise only (returns a fuel-flow rate, not a mission fuel mass)             |
    | aircraft payload      | considered implicitly via the total aircraft mass input                     |
    | climb/descent         | not modelled                                                                |
    | reserve fuel uplift   | not applicable                                                              |
    | diversion fuel uplift | not applicable                                                              |

    References
    ----------
    Turgut, E. T., Cavcar, M., Usanmaz, O., Canarslanlar, A. O., Dogeroglu, T., Armutlu, K., & Yay, O. D. (2014).
    Fuel flow analysis for the cruise phase of commercial aircraft on domestic routes.
    _Aerospace Science and Technology_, 37, 1–9.
    doi:[10.1016/j.ast.2014.04.012](https://doi.org/10.1016/j.ast.2014.04.012)

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.reducedorder import turgut_etal
    turgut_etal.list_aircraft()
    turgut_etal.calculate(
        acft='B738',
        altitude=35000*ureg.ft,
        mass=60.3*ureg.metric_ton,
        TAS=364*ureg.knot,
    )
    ```
    """

    _regression_coefficients = {
        "A319": {
            "constant": -699.157,
            "altitude": -0.021,
            "mass": 17.732,
            "tas": 6.696,
        },
        "A320": {
            "constant": -621.171,
            "altitude": -0.022,
            "mass": 18.655,
            "tas": 6.513,
        },
        "A321": {
            "constant": -1067.277,
            "altitude": -0.024,
            "mass": 21.251,
            "tas": 7.706,
        },
        "B737": {
            "constant": -713.932,
            "altitude": -0.025,
            "mass": 18.670,
            "tas": 6.964,
        },
        "B738": {
            "constant": -708.506,
            "altitude": -0.024,
            "mass": 16.633,
            "tas": 7.289,
        },
        "Airbus": {
            "constant": -1171.308,
            "altitude": -0.024,
            "mass": 27.007,
            "tas": 6.870,
        },
        "Boeing": {
            "constant": -902.088,
            "altitude": -0.025,
            "mass": 20.591,
            "tas": 7.528,
        },
        "Overall": {
            "constant": -1053.146,
            "altitude": -0.024,
            "mass": 24.956,
            "tas": 6.915,
        },
    }

    @staticmethod
    def list_aircraft() -> list[str]:
        """
        Returns a sorted list of available regression models.

        In addition to the individual aircraft designators (`A319`, `A320`, `A321`, `B737`, `B738`),
        the grouped models `Airbus` (all Airbus), `Boeing` (all Boeing) and `Overall` (all aircraft)
        are available.
        """
        return sorted(turgut_etal._regression_coefficients.keys())

    @staticmethod
    @ureg.check(
        None,  # acft
        "[length]",  # altitude
        "[mass]",  # mass
        "[speed]",  # TAS
    )
    def calculate(
        acft: str,
        altitude: pint.Quantity,
        mass: pint.Quantity,
        TAS: pint.Quantity,
    ) -> pint.Quantity:
        """
        Given a regression model, cruise altitude, aircraft mass and true airspeed, calculates the cruise fuel-flow rate.

        Parameters
        ----------
        acft : str
            Regression model to use (see `list_aircraft()`)
        altitude : pint.Quantity
            Cruise altitude [length]
        mass : pint.Quantity
            Aircraft mass [mass]
        TAS : pint.Quantity
            True airspeed [speed]

        Returns
        -------
        pint.Quantity
            Cruise fuel-flow rate [kg/h]

        Raises
        ------
        ValueError
            If the regression model is not found in the model data.
        ValueError
            If altitude, mass or true airspeed are not greater than zero.

        Warnings
        --------
        This function returns a cruise fuel-flow **rate** (kg/h), not a total mission fuel mass.
        """
        if acft not in turgut_etal._regression_coefficients:
            raise ValueError(
                f"Regression model '{acft}' not found in model data. Please select one of the following: {turgut_etal.list_aircraft()}"
            )
        if altitude <= 0 * ureg.m:
            raise ValueError("Cruise altitude must be greater than zero.")
        if mass <= 0 * ureg.kg:
            raise ValueError("Aircraft mass must be greater than zero.")
        if TAS <= 0 * ureg.knot:
            raise ValueError("True airspeed must be greater than zero.")

        coef = turgut_etal._regression_coefficients[acft]
        h = altitude.to("ft").magnitude
        m = mass.to("metric_ton").magnitude
        v = TAS.to("knot").magnitude

        ff = (
            coef["constant"] + coef["altitude"] * h + coef["mass"] * m + coef["tas"] * v
        )
        return ff * ureg("kg / hour")


def models_for_aircraft(acft: str) -> list[str]:
    """
    Given an aircraft type, returns a sorted list of the reduced-order models in this module that support it.

    A model supports an aircraft if the exact string `acft` is returned by that model's
    `list_aircraft()` method. Each returned name is a class in `jetfuelburn.reducedorder`
    whose `calculate()` method accepts that aircraft.

    Note that models which are not keyed by aircraft type (e.g. `montlaur_etal` and `sacchi_etal`,
    which select their regression from seat count or passenger capacity) do not expose an
    `list_aircraft()` method and are therefore never included.

    Parameters
    ----------
    acft : str
        ICAO Aircraft Designator, exactly as returned by a model's `list_aircraft()` (e.g. `A320`).

    Returns
    -------
    list[str]
        Sorted names of the supporting models (e.g. `['seymour_etal', 'yanto_etal']`),
        empty if no model supports the given aircraft.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.reducedorder import models_for_aircraft
    models_for_aircraft('A320')
    ```
    """
    matches = []
    for name, obj in list(globals().items()):
        if not isinstance(obj, type) or obj.__module__ != __name__:
            continue
        list_aircraft = getattr(obj, "list_aircraft", None)
        if not callable(list_aircraft):
            continue
        supported = list_aircraft()
        if isinstance(supported, (list, tuple)) and acft in supported:
            matches.append(name)
    return sorted(matches)


# Deprecated aliases of methods renamed in jetfuelburn 4.0.0 (to be removed in 5.0.0).
from jetfuelburn.utility.code import _add_deprecated_method_aliases

for _cls in (montlaur_etal, sacchi_etal):
    _add_deprecated_method_aliases(_cls, {"calculate_fuel_consumption": "calculate"})
for _cls in (
    yanto_etal,
    lee_etal,
    seymour_etal,
    aim2015,
    eea_emission_inventory_2009,
    myclimate,
):
    _add_deprecated_method_aliases(
        _cls,
        {
            "calculate_fuel_consumption": "calculate",
            "available_aircraft": "list_aircraft",
        },
    )
del _cls
