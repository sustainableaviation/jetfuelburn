import pytest
import jetfuelburn


def test_breguet():
    from jetfuelburn.breguet import calculate_fuel_consumption_range_equation
    assert callable(calculate_fuel_consumption_range_equation)


def test_diagrams():
    from jetfuelburn.diagrams import calculate_fuel_consumption_payload_range
    assert callable(calculate_fuel_consumption_payload_range)


def test_averages():
    import jetfuelburn.statistics

    from jetfuelburn.statistics import usdot
    assert callable(usdot.available_years)
    assert callable(usdot.available_aircraft)
    assert callable(usdot.calculate_fuel_consumption_per_seat)
    assert callable(usdot.calculate_fuel_consumption_per_weight)


def test_reducedorder():
    import jetfuelburn.reducedorder
    
    from jetfuelburn.reducedorder import yanto_etal
    assert callable(yanto_etal.available_aircraft)
    assert callable(yanto_etal.calculate_fuel_consumption)
    
    from jetfuelburn.reducedorder import lee_etal
    assert callable(lee_etal.available_aircraft)
    assert callable(lee_etal.calculate_fuel_consumption)
    
    from jetfuelburn.reducedorder import seymour_etal
    assert callable(seymour_etal.available_aircraft)
    assert callable(seymour_etal.calculate_fuel_consumption)
    
    from jetfuelburn.reducedorder import aim2015
    assert callable(aim2015.available_aircraft)
    assert callable(aim2015.calculate_fuel_consumption)

    from jetfuelburn.reducedorder import myclimate
    assert callable(myclimate.available_aircraft)
    assert callable(myclimate.calculate_fuel_consumption)

def test_combined():
    from jetfuelburn.combined import calculate_fuel_consumption_combined_model
    assert callable(calculate_fuel_consumption_combined_model)


def test_aux_physics():
    import jetfuelburn.aux.physics
    
    from jetfuelburn.aux.physics import _calculate_atmospheric_conditions
    assert callable(_calculate_atmospheric_conditions)
    
    from jetfuelburn.aux.physics import _calculate_dynamic_pressure
    assert callable(_calculate_dynamic_pressure)
    
    from jetfuelburn.aux.physics import _calculate_aircraft_velocity
    assert callable(_calculate_aircraft_velocity)


def test_aux_allocation():
    import jetfuelburn.aux.allocation
    
    from jetfuelburn.aux.allocation import footprint_allocation_by_area
    assert callable(footprint_allocation_by_area)


def test_aux_tests():
    import jetfuelburn.aux.tests
    
    from jetfuelburn.aux.tests import approx_with_units
    assert callable(approx_with_units)
    
    from jetfuelburn.aux.tests import approx_dict
    assert callable(approx_dict)
    
    from jetfuelburn.aux.tests import approx_dict_of_dict
    assert callable(approx_dict_of_dict)