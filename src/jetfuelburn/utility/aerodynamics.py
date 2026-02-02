# %%
import math
import json
import csv
from importlib import resources
from jetfuelburn.utility.math import _interpolate
from jetfuelburn.utility.physics import (
    _calculate_dynamic_pressure,
    _calculate_aircraft_velocity
)
from jetfuelburn import ureg


class jsbsim_drag_polars:
    r"""
    The class implements a component-based drag polar model derived from open-source JSBSim flight dynamics data.
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
        '[force]', # lift
        '[]', # Mach number
        '[length]', # altitude
    )
    def calculate_drag(
        acft: str,
        L: float,
        M: float,
        H: float,
    ) -> dict:
        r"""
        asdf
        """        
        if acft not in jsbsim_drag_polars._aircraft_data:
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data.")
        
        data = jsbsim_drag_polars._aircraft_data[acft]
        
        S = data["wing_area_sqft"] * ureg.square_feet
        q = _calculate_dynamic_pressure(
            speed=_calculate_aircraft_velocity(M, H),
            altitude=H
        )
        C_L = L / (q * S)
        
        lift_by_alpha: dict = data["lift_table"]
        alpha_rad = _interpolate(
            x_val=C_L.magnitude,
            x_list=lift_by_alpha["cl"],
            y_list=lift_by_alpha["alpha"]
        )

        c_D0_by_alpha: dict = data["cd0_table"]
        c_D_parasitic = _interpolate(
            x_val=alpha_rad,
            x_list=c_D0_by_alpha["alpha"],
            y_list=c_D0_by_alpha["cd0"]
        )

        wave_drag_by_mach: dict = data["wave_drag_table"]
        c_D_wave = _interpolate(
            x_val=M,
            x_list=wave_drag_by_mach["mach"],
            y_list=wave_drag_by_mach["cd_wave"]
        )

        c_D_induced = data["k_factor"] * (C_L ** 2)
        c_D_total = c_D_parasitic + c_D_induced + c_D_wave
        
        D = q * S * c_D_total
        
        return D
    


class openap_drag_polars:
    r"""
    The class implements a low-speed drag polar model based on data published with the OpenAP model.

    Warning
    -------
    The data used in this model is based on a XXX stoachastic model based on ADS-B data.....

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

    # Parsed from your CSV
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
    @ureg.check(
        None,
        '[force]', # lift
        '[]', # Mach number
        '[length]', # altitude
    )
    def calculate_drag(
        acft: str,
        L: float,
        M: float,
        H: float,
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

        | Symbol | Dimension             | Description                |
        |--------|-----------------------|----------------------------|
        | D      | [force]               | Drag force                 |
        | q      | [pressure]            | Dynamic pressure           |
        | S      | [area]                | Wing reference area        |
        | C_D    | [dimensionless]       | Total drag coefficient     |
        | C_{D0} | [dimensionless]       | Zero-lift drag coefficient |
        | K      | [dimensionless]       | Induced drag factor        |
        | C_L    | [dimensionless]       | Lift coefficient           |
        | L      | [force]               | Lift force                 |

        See Also
        --------
        [OpenAP Model](https://openap.dev)

        References
        ----------
        - Eqn. 7.1, 7.5 and 7.14 in 
        Young, T. M. (2018). 
        Performance of the Jet Transport Airplane. 
        _John Wiley & Sons_. 
        doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)
        - [`openap/data/aircraft`](https://github.com/TUDelft-CNS-ATM/openap/tree/master/openap/data/aircraft)

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B737', etc.)
        L : float (force)
            Lift force
        M : float (dimensionless)
            Mach number
        H : float (length)
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
            H=35000*ureg.feet,
        )
        ```
        """
        if acft not in openap_drag_polars._aircraft_data:
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data.")
        if M <= 0:
            raise ValueError("Mach number must be greater than zero.")
        if H < 0 * ureg.meter:
            raise ValueError("Altitude must be greater than or equal to zero.")
        if L <= 0 * ureg.newton:
            raise ValueError("Lift force must be greater than zero.")

        data = openap_drag_polars._aircraft_data[acft]
        
        S = data["wing_area_m2"] * ureg('m^2')
        q = _calculate_dynamic_pressure(
            speed=_calculate_aircraft_velocity(M, H),
            altitude=H
        )
        C_L = L / (q * S)
        CD0 = data["CD0"]
        K = data["K"]

        C_D_total = CD0 + K * (C_L ** 2)

        D = q * S * C_D_total
        D = D.to('N')

        return D