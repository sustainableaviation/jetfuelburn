# %%
import pint
ureg = pint.get_application_registry()
import json
from importlib import resources


class usdot():
    """
    This class contains methods to process, analyze and use statistical data on aircraft fuel consumption
    from the US Department of Transport (US DOT) based on the "T2" dataset.

    `Air Carrier Summary : T2: U.S. Air Carrier TRAFFIC And Capacity Statistics`

    _extended_summary_

    Notes
    -----
    Required data must be downloaded from the US Department of Transport:
    - ["AircraftType": `L_AIRCRAFT_TYPE.csv`]()
    - ["Data Tools: Download": `T_SCHEDULE_T2.csv`]()

    See Also
    --------
    Additional information can be found at:
    - [US DOT: BTS: Air Carrier Summary Data (Form 41 and 298C Summary Data)](https://www.transtats.bts.gov/Tables.asp?QO_VQ=EGD&QO)
    - [US DOT: BTS: Air Carrier Summary Data: T2 (U.S. Air Carrier Traffic And Capacity Statistics by Aircraft Type)](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FIH)
    """

    _aircraft_data = {}
    with resources.open_text("jetfuelburn.data.USDOT.2023", "USDOT_data_2023.json") as file:
        _aircraft_data = json.load(file)

    @staticmethod
    def available_aircraft() -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(usdot._aircraft_data.keys())
    
    @staticmethod
    @ureg.check(
        None,
        '[length]',
        '[mass]',
    )
    def calculate_fuel_consumption_per_weight(
        acft: str,
        R: float,
        W: float,
    ) -> dict:
        r"""
        """
        if R.magnitude < 0 or W.magnitude < 0:
            raise ValueError(f"Range and/or weight must not be negative.")
        else:
            R = R.to(ureg('km'))
            W = W.to(ureg('kg'))

        if acft not in usdot._aircraft_data:
            raise ValueError(f"US DOT Aircraft Designator '{acft}' not found in model data.")
        else:
            aircraft_data = usdot._aircraft_data[acft]

        fuelburn = (aircraft_data['Fuel/Revenue Weight Distance'] * ureg('1/km')) * R * W
        fuelburn = fuelburn.to(ureg('kg'))

        return fuelburn
    

    @staticmethod
    @ureg.check(
        None,
        '[length]',
    )
    def calculate_fuel_consumption_per_seat(
        acft: str,
        R: float,
    ) -> dict:
        r"""
        """
        if R.magnitude < 0:
            raise ValueError(f"Range must not be negative.")
        else:
            R = R.to(ureg('km'))

        if acft not in usdot._aircraft_data:
            raise ValueError(f"US DOT Aircraft Designator '{acft}' not found in model data.")
        else:
            aircraft_data = usdot._aircraft_data[acft]

        fuelburn = (aircraft_data['Fuel/Revenue Seat Distance'] * ureg('kg/km')) * R
        fuelburn = fuelburn.to(ureg('kg'))

        return fuelburn