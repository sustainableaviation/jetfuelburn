"""JetFuelBurn: fuel burn estimation for commercial aircraft.

`ureg` is the unit registry of the package. Build quantities with it, e.g. `100 * ureg.kg`.
"""

# https://pint.readthedocs.io/en/stable/getting/pint-in-your-projects.html#using-pint-in-your-projects
from pint import UnitRegistry, set_application_registry

ureg = UnitRegistry()
set_application_registry(ureg)

__version__ = "4.0.0"
