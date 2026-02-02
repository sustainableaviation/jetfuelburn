# https://pint.readthedocs.io/en/stable/getting/pint-in-your-projects.html#using-pint-in-your-projects
from pint import UnitRegistry
ureg = UnitRegistry()
g = 9.80665 * ureg.meter / (ureg.second ** 2)  # acceleration due to gravity

__version__ = "2.0.0"