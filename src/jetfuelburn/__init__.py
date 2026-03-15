# https://pint.readthedocs.io/en/stable/getting/pint-in-your-projects.html#using-pint-in-your-projects
from pint import UnitRegistry, set_application_registry
ureg = UnitRegistry()
set_application_registry(ureg)

__version__ = "2.1.0"
