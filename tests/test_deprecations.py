"""
Tests for the deprecated aliases of names renamed or replaced in jetfuelburn 4.0.0.
Every old name of the 3.4.0 API must keep working and raise a DeprecationWarning.
"""

import importlib
import inspect

import pytest
from jetfuelburn import ureg
from jetfuelburn import reducedorder, statistics
from jetfuelburn.utility import aerodynamics

# (class, old method name, new method name)
METHOD_ALIASES = (
    [
        (cls, "calculate_fuel_consumption", "calculate")
        for cls in (
            reducedorder.montlaur_etal,
            reducedorder.sacchi_etal,
            reducedorder.yanto_etal,
            reducedorder.lee_etal,
            reducedorder.seymour_etal,
            reducedorder.aim2015,
            reducedorder.eea_emission_inventory_2009,
            reducedorder.myclimate,
        )
    ]
    + [
        (cls, "available_aircraft", "list_aircraft")
        for cls in (
            reducedorder.yanto_etal,
            reducedorder.lee_etal,
            reducedorder.seymour_etal,
            reducedorder.aim2015,
            reducedorder.eea_emission_inventory_2009,
            reducedorder.myclimate,
            statistics.usdot,
            aerodynamics.poll_schumann_drag_polars,
        )
    ]
    + [
        (statistics.usdot, "available_years", "list_years"),
        (
            statistics.usdot,
            "calculate_fuel_consumption_per_weight",
            "calculate_per_weight",
        ),
        (statistics.usdot, "calculate_fuel_consumption_per_seat", "calculate_per_seat"),
    ]
)

# (module, old name, new name)
MODULE_ALIASES = [
    ("jetfuelburn.rangeequation", "calculate_fuel_consumption_breguet", "range_equation.calculate"),
    ("jetfuelburn.rangeequation", "calculate_fuel_consumption_breguet_improved", "range_equation.calculate_improved"),
    ("jetfuelburn.rangeequation", "calculate_fuel_consumption_stepclimb_integration", "range_equation.calculate_stepclimb_integration"),
    ("jetfuelburn.rangeequation", "calculate_fuel_consumption_stepclimb_arctan", "range_equation.calculate_stepclimb_arctan"),
    ("jetfuelburn.diagrams", "calculate_fuel_consumption_payload_range", "payload_range.calculate"),
    ("jetfuelburn.utility.aerodynamics", "openap_drag_polars", "poll_schumann_drag_polars"),
    ("jetfuelburn.utility.aerodynamics", "jsbsim_drag_polars", "poll_schumann_drag_polars"),
    ("jetfuelburn.figures.aerodynamics", "figure_openap_dragpolar", "figure_poll_schumann_dragpolar"),
    ("jetfuelburn.figures.aerodynamics", "figure_jsbsim_dragpolar_mach_effects", "figure_poll_schumann_dragpolar"),
]  # fmt: skip


def _resolve(obj, dotted_name):
    for part in dotted_name.split("."):
        obj = getattr(obj, part)
    return obj


@pytest.mark.parametrize(
    "cls, old, new", METHOD_ALIASES, ids=lambda x: getattr(x, "__name__", x)
)
def test_method_alias_forwards_with_warning(cls, old, new):
    alias = getattr(cls, old)
    # the alias wraps the new method unchanged (== also matches bound classmethods)
    assert alias.__wrapped__ == getattr(cls, new)
    if not inspect.signature(getattr(cls, new)).parameters:
        with pytest.warns(DeprecationWarning, match=f"{cls.__name__}.{new}"):
            assert alias() == getattr(cls, new)()


def test_method_alias_result():
    with pytest.warns(DeprecationWarning, match="seymour_etal.calculate"):
        old = reducedorder.seymour_etal.calculate_fuel_consumption(
            acft="B738", R=1000 * ureg.km
        )
    assert old == reducedorder.seymour_etal.calculate(acft="B738", R=1000 * ureg.km)


@pytest.mark.parametrize("module, old, new", MODULE_ALIASES, ids=lambda x: x)
def test_module_alias_returns_replacement_with_warning(module, old, new):
    mod = importlib.import_module(module)
    with pytest.warns(DeprecationWarning, match=new.replace(".", r"\.")):
        replacement = getattr(mod, old)
    assert replacement is _resolve(mod, new)


def test_module_alias_from_import():
    with pytest.warns(DeprecationWarning, match="range_equation.calculate"):
        from jetfuelburn.rangeequation import (
            calculate_fuel_consumption_breguet,
        )  # noqa: F401


def test_unknown_module_attribute_raises():
    with pytest.raises(AttributeError):
        aerodynamics.does_not_exist
