# %%
import math
import json
from importlib import resources
from jetfuelburn.utility.math import _interpolate
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
        return sorted(jsbsim_drag_polar._aircraft_data.keys())

    @staticmethod
    @ureg.check(
        None,
        None,
        None,
    )
    def calculate_drag(
        acft: str,
        CL: float,
        Mach: float,
    ) -> dict:
        r"""
        Given an aircraft name, Lift Coefficient (CL), and Mach number, calculates the total Drag Coefficient (CD).

        The calculation follows a three-step process:
        1. **Inverse Lift Lookup:** Finds the Angle of Attack ($\alpha$) required for the requested $C_L$.
        2. **Parasite Drag Lookup:** Finds $C_{D0}$ based on that $\alpha$.
        3. **Wave Drag Lookup:** Finds compressibility penalties based on Mach.

        | Symbol     | Dimension         | Description                                                            |
        |------------|-------------------|------------------------------------------------------------------------|
        | $C_D$      | [dimensionless]   | Total Drag Coefficient                                                 |
        | $C_L$      | [dimensionless]   | Lift Coefficient                                                       |
        | $M$        | [dimensionless]   | Mach Number                                                            |

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'B737', 'B788').
        CL : float or ureg.Quantity
            Lift Coefficient [dimensionless].
        Mach : float or ureg.Quantity
            Mach Number [dimensionless].

        Returns
        -------
        dict
            'CD_total' : ureg.Quantity
                Total Drag Coefficient [dimensionless]
            'CD_parasite' : ureg.Quantity
                Base parasite drag component [dimensionless]
            'CD_induced' : ureg.Quantity
                Induced drag component [dimensionless]
            'CD_wave' : ureg.Quantity
                Compressibility/Mach drag component [dimensionless]
            'alpha_rad' : ureg.Quantity
                Angle of Attack [radians]

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        """
        
        # Ensure inputs are magnitude only if they were passed as Quantities
        if hasattr(CL, "magnitude"): CL = CL.magnitude
        if hasattr(Mach, "magnitude"): Mach = Mach.magnitude

        if acft not in jsbsim_drag_polar._aircraft_data:
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data.")
        
        data = jsbsim_drag_polar._aircraft_data[acft]
        
        # 1. Get Alpha required for this Lift (Inverse Interpolation: x=CL, y=Alpha)
        # Note: The JSON stores Lift as x=Alpha, y=CL. We swap them for the lookup.
        lift_table = data["lift_table"]
        alpha_rad = jsbsim_drag_polar._interpolate(CL, lift_table["cl"], lift_table["alpha"])

        # 2. Get Parasite Drag (CD0) for that Alpha
        cd0_table = data["cd0_table"]
        cd_parasite = jsbsim_drag_polar._interpolate(alpha_rad, cd0_table["alpha"], cd0_table["cd0"])

        # 3. Get Wave Drag for this Mach
        wave_table = data["wave_drag_table"]
        cd_wave = jsbsim_drag_polar._interpolate(Mach, wave_table["mach"], wave_table["cd_wave"])

        # 4. Calculate Induced Drag (k * CL^2)
        cd_induced = data["k_factor"] * (CL ** 2)

        # 5. Sum Total
        cd_total = cd_parasite + cd_induced + cd_wave

        return {
            'CD_total': cd_total * ureg('dimensionless'),
            'CD_parasite': cd_parasite * ureg('dimensionless'),
            'CD_induced': cd_induced * ureg('dimensionless'),
            'CD_wave': cd_wave * ureg('dimensionless'),
            'alpha_rad': alpha_rad * ureg('radian')
        }