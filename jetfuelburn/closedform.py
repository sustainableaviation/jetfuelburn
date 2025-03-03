import math
import csv
import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

from aux.physics import _calculate_dynamic_pressure

class poll_et_al:
    r"""

    References
    ----------
    - Poll, D. I. A., & Schumann, U. (2025).
    An estimation method for the fuel burn and other performance characteristics of civil transport aircraft; part 3 full flight profile when the trajectory is specified.
    _The Aeronautical Journal_, 1-37.
    doi:[10.1017/aer.2024.141](https://doi.org/10.1017/aer.2024.141)
    - Poll, D. I. A., & Schumann, U. (2021).
    An estimation method for the fuel burn and other performance characteristics of civil transport aircraft during cruise: part 2, determining the aircraft’s characteristic parameters.
    _The Aeronautical Journal_, 125(1284), 296-340.
    doi:[10.1017/aer.2020.124](https://doi.org/10.1017/aer.2020.124)
    - Poll, D. I. A., & Schumann, U. (2021).
    An estimation method for the fuel burn and other performance characteristics of civil transport aircraft in the cruise. Part 1 fundamental quantities and governing relations for a general atmosphere.
    _The Aeronautical Journal_, 125(1284), 257-295.
    doi:[10.1017/aer.2020.62](https://doi.org/10.1017/aer.2020.62)
    """

    dict_coefficients = {}
    with open("data/PS2025/table_1.csv", mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            variable = row.pop('Variable')
            dict_coefficients[variable] = {key: float(value) for key, value in row.items()}
    

    def __init__(self):
        self.dict_design_optimum_coefficients = {
            'A30B': {'eta_0_DO': 0.276, 'C_T_DO': 0.0350, 'S_ref': 260.0, 'BPR': 4.6},
        }

    def available_aircraft(self) -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        See also Table 5 in Yanto and Liem (2017).
        """
        return sorted(self.dict_regression_coefficients.keys())

    def calculate_fuel_consumption(
        acft: str,
        M_flight: float,
        altitude: float,
    ):
        
        LCV = 43.0e6
        eta_0_DO = self.dict_design_optimum_coefficients[acft]['eta_0_DO']
        C_T_DO = self.dict_design_optimum_coefficients[acft]['C_T_DO']
        S_ref = self.dict_design_optimum_coefficients[acft]['S_ref']
        BPR = self.dict_design_optimum_coefficients[acft]['BPR']

        # TODO
        #pressure = (alt)
        #speed_of_sound = (alt)


        eta_2 = 0.65 * (1 - 0.035 * BPR) # Eqn (29) in Poll et al. (2025)
        eta_0_B = eta_0_DO * (M_flight / M_DO) ** eta_2 # Eqn (27) in Poll et al. (2025)
        C_T_B = C_T_DO * ((1 + 0.55 * M_flight) / (1 + 0.55 * M_DO)) * (M_DO / M_flight) ** 2 # Eqn (28) in Poll et al. (2025)
        m_f_dot = (gamma/2) * (C_T_B / eta_0_B) * (M_flight ** 3) * ()

        #what about weight?!