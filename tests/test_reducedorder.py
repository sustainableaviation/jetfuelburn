import pytest

from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.reducedorder import yanto_etal, aim2015, seymour_etal, lee_etal
from .fixtures.reducedorder import (
    fixture_yanto_B739,
    fixture_aim2015_B787,
    fixture_seymour_B738,
    fixture_lee_B732
)


def test_yanto_etal_B739(fixture_yanto_B739):
    make_case, params = fixture_yanto_B739
    
    for r, pl in params:
        input_data, expected_output = make_case(r, pl)
        calculated_output = yanto_etal.calculate_fuel_consumption(
            acft=input_data['acft'],
            R=input_data['R'],
            PL=input_data['PL'],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to('kg'),
            rel=0.075
        )

def test_aim2015(fixture_aim2015_B787):
    make_case, distances = fixture_aim2015_B787
    
    for d in distances:
        input_data, expected_output = make_case(d)
        calculated_output = aim2015.calculate_fuel_consumption(
            acft_size_class=input_data['acft_size_class'],
            D_climb=input_data['D_climb'],
            D_cruise=input_data['D_cruise'],
            D_descent=input_data['D_descent'],
            PL=input_data['PL']
        )
        assert approx_with_units(
            value_check=sum(calculated_output.values()),
            value_expected=expected_output.to('kg'),
            rel=0.075
        )

def test_seymour(fixture_seymour_B738):
    make_case, ranges = fixture_seymour_B738
    
    for r in ranges:
        input_data, expected_output = make_case(r)
        calculated_output = seymour_etal.calculate_fuel_consumption(
            acft=input_data['acft'],
            R=input_data['R'],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to('kg'),
            rel=0.075
        )