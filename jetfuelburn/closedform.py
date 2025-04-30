import math
import csv
from jetfuelburn import ureg
from jetfuelburn.aux.physics import _calculate_dynamic_pressure

def poll_et_al() -> None:
    r"""
    This function will be implemented in a later version of `jetfuelburn`.
    It will use the closed-form solution for the fuel burn estimation method developed by Poll et al.:
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
    return NotImplementedError