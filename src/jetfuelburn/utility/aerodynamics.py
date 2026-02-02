# %%
import math
import json
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
        if hasattr(L, "magnitude"): L = L.magnitude
        if hasattr(M, "magnitude"): M = M.magnitude

        if acft not in jsbsim_drag_polars._aircraft_data:
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data.")
        
        data = jsbsim_drag_polars._aircraft_data[acft]
        
        S = data["wing_area_sqft"] * ureg.square_feet
        q = _calculate_dynamic_pressure(
            speed=_calculate_aircraft_velocity(M, H),
            altitude=H
        )
        C_L = L * q * S
        
        lift_by_alpha: dict = data["lift_table"]
        alpha_rad = _interpolate(
            x_val=C_L,
            x_list=lift_by_alpha["cl"],
            y_list=lift_by_alpha["alpha"]
        )

        c_D0_by_alpha: dict = data["c_D0_table"]
        c_D_parasitic = _interpolate(
            x_val=alpha_rad,
            x_list=c_D0_by_alpha["alpha"],
            y_list=c_D0_by_alpha["c_D0"]
        )

        wave_drag_by_mach: dict = data["wave_drag_table"]
        c_D_wave = _interpolate(
            x_val=M,
            x_list=wave_drag_by_mach["mach"],
            y_list=wave_drag_by_mach["c_D_wave"]
        )

        c_D_induced = data["k_factor"] * (C_L ** 2)
        c_D_total = c_D_parasitic + c_D_induced + c_D_wave
        
        D = q * S * c_D_total
        
        return D