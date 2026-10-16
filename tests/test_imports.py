import pytest
import jetfuelburn


def test_rangeequation():
    from jetfuelburn.rangeequation import range_equation

    assert callable(range_equation.calculate_stepclimb_integration)
    assert callable(range_equation.calculate_stepclimb_arctan)
    assert callable(range_equation.calculate_improved)
    assert callable(range_equation.calculate)


def test_diagrams():
    from jetfuelburn.diagrams import payload_range

    assert callable(payload_range.calculate)


def test_averages():
    import jetfuelburn.statistics

    from jetfuelburn.statistics import usdot

    assert callable(usdot.list_years)
    assert callable(usdot.list_aircraft)
    assert callable(usdot.calculate_per_seat)
    assert callable(usdot.calculate_per_weight)


def test_reducedorder():
    import jetfuelburn.reducedorder

    from jetfuelburn.reducedorder import yanto_etal

    assert callable(yanto_etal.list_aircraft)
    assert callable(yanto_etal.calculate)

    from jetfuelburn.reducedorder import lee_etal

    assert callable(lee_etal.list_aircraft)
    assert callable(lee_etal.calculate)

    from jetfuelburn.reducedorder import seymour_etal

    assert callable(seymour_etal.list_aircraft)
    assert callable(seymour_etal.calculate)

    from jetfuelburn.reducedorder import aim2015

    assert callable(aim2015.list_aircraft)
    assert callable(aim2015.calculate)

    from jetfuelburn.reducedorder import myclimate

    assert callable(myclimate.list_aircraft)
    assert callable(myclimate.calculate)


def test_aux_physics():
    import jetfuelburn.utility.physics

    from jetfuelburn.utility.physics import _calculate_atmospheric_temperature

    assert callable(_calculate_atmospheric_temperature)

    from jetfuelburn.utility.physics import _calculate_atmospheric_density

    assert callable(_calculate_atmospheric_density)

    from jetfuelburn.utility.physics import _calculate_dynamic_pressure

    assert callable(_calculate_dynamic_pressure)

    from jetfuelburn.utility.physics import _calculate_speed_of_sound

    assert callable(_calculate_speed_of_sound)

    from jetfuelburn.utility.physics import _calculate_airspeed_from_mach

    assert callable(_calculate_airspeed_from_mach)


def test_aux_allocation():
    import jetfuelburn.utility.allocation

    from jetfuelburn.utility.allocation import footprint_allocation_by_area

    assert callable(footprint_allocation_by_area)


def test_aux_tests():
    import jetfuelburn.utility.tests

    from jetfuelburn.utility.tests import approx_with_units

    assert callable(approx_with_units)

    from jetfuelburn.utility.tests import approx_dict

    assert callable(approx_dict)

    from jetfuelburn.utility.tests import approx_dict_of_dict

    assert callable(approx_dict_of_dict)


def test_aux_math():
    import jetfuelburn.utility.mathematics

    from jetfuelburn.utility.mathematics import _interpolate

    assert callable(_interpolate)


def test_aux_code():
    import jetfuelburn.utility.code

    from jetfuelburn.utility.code import _validate_physics_function_parameters

    assert callable(_validate_physics_function_parameters)

    from jetfuelburn.utility.code import _normalize_physics_function_or_scalar

    assert callable(_normalize_physics_function_or_scalar)


def test_aux_engines():
    import jetfuelburn.utility.engines

    from jetfuelburn.utility.engines import calculate_corrected_tsfc

    assert callable(calculate_corrected_tsfc)


def test_aux_aerodynamics():
    import jetfuelburn.utility.aerodynamics

    from jetfuelburn.utility.aerodynamics import poll_schumann_drag_polars

    assert callable(poll_schumann_drag_polars.list_aircraft)
    assert callable(poll_schumann_drag_polars.get_basic_drag_parameters)
    assert callable(poll_schumann_drag_polars.calculate_drag)
    assert callable(poll_schumann_drag_polars.calculate_lift_to_drag)
    assert callable(poll_schumann_drag_polars.calculate_lift_to_drag_binder_function)
