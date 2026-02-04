import inspect
from typing import Callable, Union
from jetfuelburn import ureg

# Ensure Q_ is available
Q_ = ureg.Quantity

class IntegratedRangeCalculator:
    """
    Performs numerical integration of the Specific Air Range (SAR) to estimate 
    cruise performance. Supports both static and dynamic TSFC models.
    """
    def __init__(self, 
                 drag_function: Callable, 
                 aircraft_designator: str, 
                 tsfc: Union[ureg.Quantity, Callable]):
        # ... (Same initialization code as before) ...
        if not callable(drag_function):
            raise TypeError("drag_function must be callable.")
        self._validate_signature(drag_function, {'acft', 'L', 'M', 'H'})
        self.drag_function = drag_function
        
        if isinstance(tsfc, ureg.Quantity):
            self.tsfc_function = lambda M, H, F: tsfc
        elif callable(tsfc):
            self._validate_signature(tsfc, {'M', 'H', 'F'})
            self.tsfc_function = tsfc
        else:
            raise TypeError("tsfc must be a pint.Quantity or a Callable.")

        self.acft_id = aircraft_designator

    def _validate_signature(self, func: Callable, required_params: set):
        sig = inspect.signature(func)
        func_params = sig.parameters.keys()
        missing = required_params - func_params
        if missing:
            raise ValueError(f"Function missing parameters: {missing}")

    def compute_integrated_range(self, start_weight, end_weight, altitude, mach, num_intervals=20):
        # 1. Define Weight Stations
        start_mag = start_weight.to("lbf").magnitude
        end_mag = end_weight.to("lbf").magnitude
        step = (end_mag - start_mag) / (num_intervals - 1)
        weight_stations = [Q_(start_mag + i * step, "lbf") for i in range(num_intervals)]

        # 2. Performance Parameters
        tas = _calculate_aircraft_velocity(mach, altitude)
        ranges = [Q_(0, "nautical_mile")]
        times = [Q_(0, "hour")]
        sar_values = []
        fuel_burn_values = [] # New list for Fuel Burn per Distance

        # 3. Loop
        for W in weight_stations:
            Lift = W
            
            # A. Calculate Drag
            Drag = self.drag_function(
                acft=self.acft_id, 
                L=Lift, 
                M=mach, 
                H=altitude
            )
            
            # B. Determine TSFC
            current_tsfc = self.tsfc_function(M=mach, H=altitude, F=Drag)
            
            # C. Calculate Fuel Flow
            fuel_flow = Drag * current_tsfc
            
            # D. Specific Air Range (SAR) [Distance / Mass]
            sar = (tas / fuel_flow).to("nautical_mile / lb")
            sar_values.append(sar)

            # --- NEW: Fuel Burn per Distance [Mass / Distance] ---
            # This is simply 1 / SAR.
            # Example units: lb / nm or kg / km
            fb_dist = (1 / sar).to("lb / nautical_mile")
            fuel_burn_values.append(fb_dist)

        # 4. Integrate Range (Standard Procedure)
        cumulative_r = 0 * ureg.nautical_mile
        cumulative_t = 0 * ureg.hour
        
        for i in range(len(weight_stations) - 1):
            sar_avg = (sar_values[i] + sar_values[i+1]) / 2
            dw_force = weight_stations[i] - weight_stations[i+1]
            dw_mass = (dw_force / ureg.standard_gravity).to("lb")
            
            dr = sar_avg * dw_mass
            dt = dr / tas
            
            cumulative_r += dr
            cumulative_t += dt
            ranges.append(cumulative_r)
            times.append(cumulative_t)
            
        return {
            "weight": weight_stations,
            "range": ranges,
            "time": times,
            "sar": sar_values,
            "fuel_burn_per_distance": fuel_burn_values # Return the new metric
        }