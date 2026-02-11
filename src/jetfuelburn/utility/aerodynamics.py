# %%
import json
import csv
from importlib import resources
from typing import Callable
import functools
from jetfuelburn.utility.math import _interpolate
from jetfuelburn.utility.physics import (
    _calculate_dynamic_pressure,
    _calculate_airspeed_from_mach,
)
import pint
from jetfuelburn import ureg


class jsbsim_drag_polars:
    r"""
    The class implements a component-based drag polar model derived from open-source
    [JSBSim](https://github.com/JSBSim-Team/jsbsim) flight dynamics data.

    ```python exec="true" html="true"
    from jetfuelburn.figures.aerodynamics import figure_jsbsim_dragpolar_mach_effects
    fig = figure_jsbsim_dragpolar_mach_effects()
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    # https://pawamoy.github.io/markdown-exec/gallery/#with-plotly
    ```

    Warning
    -------
    The data used in this model is based on data collected by XXXXX

    See Also
    --------
    [`jetfuelburn.utility.aerodynamics.openap_drag_polars`][]

    References
    ----------
    Berndt, J. S., & JSBSim Development Team. (2011).
    [JSBSim: An open source, platform-independent, flight dynamics model in C++]((https://jsbsim.sourceforge.net/JSBSimReferenceManual.pdf)).
    """

    _aircraft_data = {}
    with resources.open_text("jetfuelburn.data.JSBSim", "data.json") as file:
        _aircraft_data = json.load(file)

    @staticmethod
    def available_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(jsbsim_drag_polars._aircraft_data.keys())

    @staticmethod
    @ureg.check(
        None,
        "[force]",
        "[]",
        "[length]",
    )
    def calculate_drag(
        acft: str,
        L: pint.Quantity,
        M: float | int | pint.Quantity,
        h: pint.Quantity,
    ) -> pint.Quantity:
        r"""
        Given lift, Mach number, and altitude, calculates the drag force for a specified aircraft
        using a component-based drag polar model derived from JSBSim flight dynamics data.

        Drag is calculated as:

        \begin{align*}
        D &= q \cdot S \cdot C_D \\
        C_L &= \frac{L}{q \cdot S}
        \end{align*}

        with the drag coefficient $C_D$ calculated as the sum of parasitic, induced, and wave drag components 
        (drag build-up):

        $$
        C_D = C_{D0}(\alpha) + C_{D_{i}} + C_{D_{wave}} = C_{D0}(\alpha) + k \cdot C_L^2 + C_{D_{wave}}
        $$

        where:

        | Symbol           | Dimension             | Description                             |
        |------------------|-----------------------|-----------------------------------------|
        | $D$              | [force]               | Drag force                              |
        | $L$              | [force]               | Lift force                              |
        | $q$              | [pressure]            | Dynamic pressure                        |
        | $S$              | [area]                | Wing reference area                     |
        | $C_D$            | [dimensionless]       | Total drag coefficient                  |
        | $C_{D0}$         | [dimensionless]       | Parasitic drag coefficient at zero lift |
        | $C_{D_{i}}$      | [dimensionless]       | Induced drag coefficient                |
        | $C_{D_{wave}}$   | [dimensionless]       | Wave drag coefficient                   |
        | $k$              | [dimensionless]       | Induced drag factor                     |
        | $C_L$            | [dimensionless]       | Lift coefficient                        |
        | $\alpha$         | [radians]             | Angle of attack                         |
        
        Warning
        -------
        Data is derived from JSBSim flight dynamics models, the accuracy of which may vary based on the specific aircraft and flight conditions.
        
        Notes
        -----
        In this model, the parasitic drag coefficient $C_{D0}$ is a function of angle of attack ($\alpha$), 
        which is estimated by interpolating from the lift coefficient ($C_L$) using the lift curve data.

        See Also
        --------
        [JSBSim Flight Dynamics Model on Sourceforge](https://sourceforge.net/projects/jsbsim/)

        References
        ----------
        Eqn. 7.7 in 
        Young, T. M. (2018). 
        Performance of the Jet Transport Airplane. 
        _John Wiley & Sons_. 
        doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B737', etc.)
        L : pint.Quantity (force)
            Lift force
        M : float or pint.Quantity (dimensionless)
            Mach number
        h : pint.Quantity (length)
            Altitude

        Returns
        -------
        pint.Quantity (force)
            Drag force [N]
        
        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        ValueError
            If the Mach number, altitude, or lift force are out of expected ranges (e.g., Mach number <= 0, altitude < 0, lift <= 0).
        """
        if acft not in jsbsim_drag_polars._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )

        data = jsbsim_drag_polars._aircraft_data[acft]

        S = data["wing_area_sqft"] * ureg.square_feet
        q = _calculate_dynamic_pressure(
            speed=_calculate_airspeed_from_mach(M, h), altitude=h
        )
        C_L = L / (q * S)

        lift_by_alpha: dict = data["lift_table"]
        alpha_rad = _interpolate(
            x_val=C_L.magnitude,
            x_list=lift_by_alpha["cl"],
            y_list=lift_by_alpha["alpha"],
        )

        c_D0_by_alpha: dict = data["cd0_table"]
        c_D_parasitic = _interpolate(
            x_val=alpha_rad, x_list=c_D0_by_alpha["alpha"], y_list=c_D0_by_alpha["cd0"]
        )

        wave_drag_by_mach: dict = data["wave_drag_table"]
        c_D_wave = _interpolate(
            x_val=M,
            x_list=wave_drag_by_mach["mach"],
            y_list=wave_drag_by_mach["cd_wave"],
        )

        c_D_induced = data["k_factor"] * (C_L**2)
        c_D_total = c_D_parasitic + c_D_induced + c_D_wave

        D = q * S * c_D_total

        return D

    @staticmethod
    @ureg.check(
        None,
        "[force]",  # lift
        "[]",  # Mach number
        "[length]",  # altitude
    )
    def calculate_lift_to_drag(
        acft: str,
        L: pint.Quantity,
        M: float | int | pint.Quantity,
        h: pint.Quantity,
    ) -> pint.Quantity:
        r"""
        Given lift, Mach number, and altitude,
        calculates the lift-to-drag ratio for a specified aircraft
        using the JSBSim-based drag polar model.

        See Also
        --------
        - [`jetfuelburn.utility.aerodynamics.jsbsim_drag_polars.calculate_drag`][]
        - [`jetfuelburn.utility.aerodynamics.jsbsim_drag_polars.calculate_lift_to_drag_binder_function`][]

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B737', etc.)
        L : pint.Quantity (force)
            Lift force
        M : float or pint.Quantity (dimensionless)
            Mach number
        h : pint.Quantity (length)
            Altitude

        Returns
        -------
        pint.Quantity (dimensionless)
            Lift-to-drag ratio (dimensionless)

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.

        Example
        -------
        ```pyodide install='jetfuelburn'
        import jetfuelburn
        from jetfuelburn import ureg
        from jetfuelburn.utility.aerodynamics import jsbsim_drag_polars
        L_D = jsbsim_drag_polars._calculate_lift_to_drag(
            acft='A320',
            L=60000*ureg.newton,
            M=0.78,
            h=35000*ureg.feet,
        )
        ```
        """
        if acft not in jsbsim_drag_polars._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )

        drag = jsbsim_drag_polars.calculate_drag(
            acft=acft,
            L=L,
            M=M,
            h=h,
        )
        L_D_ratio = L / drag
        L_D_ratio = L_D_ratio.to("dimensionless")

        return L_D_ratio

    @staticmethod
    def calculate_lift_to_drag_binder_function(
        acft: str,
        L: pint.Quantity | None = None,
        M: float | pint.Quantity | None = None,
        h: pint.Quantity | None = None,
    ):
        r"""
        Serves as a binder for the `_calculate_lift_to_drag` method.
        If parameters `L`, `M`, or `h` are omitted, returns a
        [Callable (partial)](https://docs.python.org/3/library/functools.html#functools.partial)
        with `acft` pre-bound.
        If all arguments are provided, performs the calculation immediately.

        Notes
        -----
        This is useful for scenarios where you want to create a reusable function for a specific aircraft,
        and then call it with different flight conditions (lift, Mach number, altitude) without having
        to specify the aircraft each time. For example:

        ```pyodide install='jetfuelburn'
        from jetfuelburn.utility.aerodynamics import jsbsim_drag_polars
        a320_lift_to_drag = jsbsim_drag_polars.calculate_lift_to_drag_binder_function(acft='A320')
        a320_lift_to_drag(L=60000*ureg.newton, M=0.78, h=35000*ureg.feet)
        ```

        See Also
        --------
        [`jetfuelburn.utility.aerodynamics.jsbsim_drag_polars._calculate_lift_to_drag`][]
        """
        if L is None or M is None or h is None:
            return functools.partial(
                jsbsim_drag_polars._calculate_lift_to_drag, acft=acft
            )
        else:
            return jsbsim_drag_polars._calculate_lift_to_drag(acft, L, M, h)


class openap_drag_polars:
    r"""
    The class implements a low-speed drag polar model based on data published with
    the [OpenAP model](https://openap.dev/).

    ```python exec="true" html="true"
    from jetfuelburn.figures.aerodynamics import figure_openap_dragpolar
    fig = figure_openap_dragpolar()
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    # https://pawamoy.github.io/markdown-exec/gallery/#with-plotly
    ```

    Warning
    -------
    The data used in this model is based on a stochastic model derived from aggregated ADS-B
    flight data. Parameters were estimated using data mining statistical methods
    to fit probability density functions to observed trajectories.

    See Also
    --------
    [`jetfuelburn.utility.aerodynamics.jsbsim_drag_polars`][]

    References
    ----------
    - Sun, J., Hoekstra, J. M., & Ellerbroek, J. (2020).
      OpenAP: An open-source aircraft performance model for air transportation studies and simulations.
      _Aerospace_, 7(8), 104.
      doi:[10.3390/aerospace7080104](https://doi.org/10.3390/aerospace7080104)
    - Sun, J., Hoekstra, J. M., & Ellerbroek, J. (2020).
      Estimating aircraft drag polar using open flight surveillance data and a stochastic total energy model.
      _Transportation Research Part C: Emerging Technologies_, 114, 391-404.
      doi:[10.1016/j.trc.2020.01.026](https://doi.org/10.1016/j.trc.2020.01.026)
    """

    _aircraft_data = {}
    with resources.open_text("jetfuelburn.data.OpenAP", "data.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            icao = row["icao_code"]
            _aircraft_data[icao] = {
                "wing_area_m2": float(row["wing_area_m2"]),
                "CD0": float(row["CD0"]),
                "K": float(row["K"]),
            }

    @staticmethod
    def available_aircraft() -> list[str]:
        r"""
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(openap_drag_polars._aircraft_data.keys())

    @staticmethod
    def get_basic_drag_parameters(acft: str) -> dict:
        r"""
        Retrieves basic aerodynamic parameters for a given aircraft based on the OpenAP drag polar model.

        See Also
        --------
        [`openap/data/aircraft`](https://github.com/TUDelft-CNS-ATM/openap/tree/master/openap/data/aircraft)

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B737', etc.)

        Returns
        -------
        dict
            A dictionary of the form:

            | Key   | Type                   |  Description                                 |
            |-------|------------------------|----------------------------------------------|
            | `S`   | `pint.Quantity` [area] | Wing reference area in square meters [m²]    |
            | `CD0` | `float`                | Zero-lift drag coefficient (dimensionless)   |
            | `K`   | `float`                | Induced drag factor (dimensionless)          |

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.

        Example
        -------
        ```pyodide install='jetfuelburn'
        from jetfuelburn.utility.aerodynamics import openap_drag_polars
        openap_drag_polars.get_basic_drag_parameters('A320')
        ```
        """
        if acft not in openap_drag_polars._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )
        data: dict = openap_drag_polars._aircraft_data[acft].copy()
        data["S"] = data.pop("wing_area_m2") * ureg("m^2")
        return data

    @staticmethod
    @ureg.check(
        None,
        "[force]",  # lift
        "[]",  # Mach number
        "[length]",  # altitude
    )
    def calculate_drag(
        acft: str,
        L: float | int,
        M: float | int,
        h: float | int,
    ) -> dict:
        r"""
        Calculates the drag force for a given aircraft based on a low-speed drag polar 
        based on data published with the OpenAP model.

        Drag is calculated as:

        \begin{align*}
        D &= q \cdot S \cdot C_D \\
        C_D &= C_{D0} + K \cdot C_L^2 \\
        C_L &= \frac{L}{q \cdot S}
        \end{align*}

        where:

        | Symbol   | Dimension             | Description                |
        |----------|-----------------------|----------------------------|
        | $D$      | [force]               | Drag force                 |
        | $q$      | [pressure]            | Dynamic pressure           |
        | $S$      | [area]                | Wing reference area        |
        | $C_D$    | [dimensionless]       | Total drag coefficient     |
        | $C_{D0}$ | [dimensionless]       | Zero-lift drag coefficient |
        | $K$      | [dimensionless]       | Induced drag factor        |
        | $C_L$    | [dimensionless]       | Lift coefficient           |
        | $L$      | [force]               | Lift force                 |

        See Also
        --------
        [OpenAP Model](https://openap.dev)

        References
        ----------
        Eqn. 7.1, 7.5 and 7.14 in 
        Young, T. M. (2018). 
        Performance of the Jet Transport Airplane. 
        _John Wiley & Sons_. 
        doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B737', etc.)
        L : float (force)
            Lift force
        M : float (dimensionless)
            Mach number
        h : float (length)
            Altitude
        
        Returns
        -------
        float (force)
            Drag force [N]

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        ValueError
            If the Mach number is less than or equal to zero.
        ValueError
            If the altitude is less than zero.
        ValueError
            If the lift force is less than or equal to zero.

        Example
        -------
        ```pyodide install='jetfuelburn'
        import jetfuelburn
        from jetfuelburn import ureg
        from jetfuelburn.utility.aerodynamics import openap_drag_polars
        drag_force = openap_drag_polars.calculate_drag(
            acft='A320',
            L=60000*ureg.newton,
            M=0.78,
            h=35000*ureg.feet,
        )
        ```
        """
        if acft not in openap_drag_polars._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )
        if M <= 0:
            raise ValueError("Mach number must be greater than zero.")
        if h < 0 * ureg.meter:
            raise ValueError("Altitude must be greater than or equal to zero.")
        if L <= 0 * ureg.newton:
            raise ValueError("Lift force must be greater than zero.")

        data = openap_drag_polars._aircraft_data[acft]

        S = data["wing_area_m2"] * ureg("m^2")
        q = _calculate_dynamic_pressure(
            speed=_calculate_airspeed_from_mach(M, h), altitude=h
        )
        C_L = L / (q * S)
        CD0 = data["CD0"]
        K = data["K"]

        C_D_total = CD0 + K * (C_L**2)

        D = q * S * C_D_total
        D = D.to("N")

        return D

    @staticmethod
    @ureg.check(
        None,
        "[force]",  # lift
        "[]",  # Mach number
        "[length]",  # altitude
    )
    def calculate_lift_to_drag(
        acft: str,
        L: pint.Quantity,
        M: float | int | pint.Quantity,
        h: pint.Quantity,
    ) -> pint.Quantity:
        r"""
        Given lift, Mach number, and altitude,
        calculates the lift-to-drag ratio for a specified aircraft
        using the OpenAP-based drag polar model.

        See Also
        --------
        - [`jetfuelburn.utility.aerodynamics.openap_drag_polars.calculate_drag`][]
        - [`jetfuelburn.utility.aerodynamics.openap_drag_polars.calculate_lift_to_drag_binder_function`][]

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B737', etc.)
        L : pint.Quantity (force)
            Lift force
        M : float or pint.Quantity (dimensionless)
            Mach number
        h : pint.Quantity (length)
            Altitude
        """
        if acft not in openap_drag_polars._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )

        drag = openap_drag_polars.calculate_drag(
            acft=acft,
            L=L,
            M=M,
            h=h,
        )
        L_D_ratio = L / drag
        L_D_ratio = L_D_ratio.to("dimensionless")
        return L_D_ratio

    @staticmethod
    def calculate_lift_to_drag_binder_function(
        acft: str,
        L: pint.Quantity | None = None,
        M: float | pint.Quantity | None = None,
        h: pint.Quantity | None = None,
    ) -> Callable | pint.Quantity:
        r"""
        Serves as a binder for the `calculate_lift_to_drag` method.
        If parameters `L`, `M`, or `h` are omitted, returns a
        [Callable (partial)](https://docs.python.org/3/library/functools.html#functools.partial)
        with `acft` pre-bound.
        If all arguments are provided, performs the calculation immediately.

        Notes
        -----
        This is useful for scenarios where you want to create a reusable function for a specific aircraft,
        and then call it with different flight conditions (lift, Mach number, altitude) without having
        to specify the aircraft each time. For example:

        ```pyodide install='jetfuelburn'
        from jetfuelburn.utility.aerodynamics import openap_drag_polars
        a320_lift_to_drag = openap_drag_polars.calculate_lift_to_drag_binder_function(acft='A320')
        a320_lift_to_drag(L=60000*ureg.newton, M=0.78, h=35000*ureg.feet)
        ```

        See Also
        --------
        [`jetfuelburn.utility.aerodynamics.openap_drag_polars.calculate_lift_to_drag`][]
        """
        if L is None or M is None or h is None:
            return functools.partial(
                openap_drag_polars.calculate_lift_to_drag, acft=acft
            )
        else:
            return openap_drag_polars.calculate_lift_to_drag(acft, L, M, h)
