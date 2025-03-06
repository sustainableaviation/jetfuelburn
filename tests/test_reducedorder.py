import pytest

from jetfuelburn import ureg

from jetfuelburn.aux.tests import approx_with_units

from .fixtures.reducedorder import (
    fixture_yanto_B739,
    fixture_aim2015_B787,
    fixture_seymour_B738,
    fixture_lee_B732_1500nmi,
    fixture_lee_B732_2000nmi
)

from jetfuelburn.reducedorder import (
    yanto_etal,
    aim2015,
    seymour_etal,
    lee_etal
)


@pytest.mark.parametrize(
    argnames="r, pl",
    argvalues=[
        (2943 * ureg.km, 7885 * ureg.kg),
        (4724 * ureg.km, 17918 * ureg.kg),
    ],
    ids=["B739_light_2943km", "B739_heavy_4724km"]
)
def test_yanto_etal_B739(r, pl, make_yanto_etal_B739_case):
    input_data, expected_output = make_yanto_etal_B739_case(r, pl)
    calculated_output = calculate_yanto_fuel(
        acft=input_data['acft'],
        R=input_data['R'],
        PL=input_data['PL'],
    )
    assert approx_with_units(
        value_check=calculated_output,
        value_expected=expected_output,
        rel=0.075
    )

@pytest.mark.parametrize(
    argnames="d",
    argvalues=[
        5000 * ureg.km,
        10000 * ureg.km,
        15000 * ureg.km,
    ],
    ids=["distance_5k_km", "distance_10k_km", "distance_15k_km"]
)
def test_aim2015(d, fixture_aim2015_B787):
    input_data, expected_output = fixture_aim2015_B787(d)
    calculated_output = aim2015.calculate_fuel_consumption(
        acft_size_class=input_data['acft_size_class'],
        D_climb=input_data['D_climb'],
        D_cruise=input_data['D_cruise'],
        D_descent=input_data['D_descent'],
        PL=input_data['PL']
    )
    assert approx_with_units(
        value_check=sum(calculated_output.values()),
        value_expected=expected_output,
        rel=0.075
    )


@pytest.mark.parametrize(
    argnames="r",
    argvalues=[
        902 * ureg.km,
        5557 * ureg.km,
    ],
    ids=["range_1000km", "range_5500km"]
)
def test_seymour(r, fixture_seymour_B738):
    input_data, expected_output = fixture_seymour_B738(r)
    calculated_output = seymour_etal.calculate_fuel_consumption(
        acft=input_data['acft'],
        R=input_data['R'],
    )
    assert approx_with_units(
        value_check=calculated_output,
        value_expected=expected_output,
        rel=0.075
    )


@pytest.mark.parametrize(
    "fixture_name",
    ["fixture_lee_B732_1500nmi", "fixture_lee_B732_2000nmi"]
)
def test_lee_etal(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data, output_data = fixture

    _, weight_payload = lee_etal.calculate_fuel(
        acft=input_data['acft'],
        W_E=input_data['W_E'],
        W_MPLD=input_data['W_MPLD'],
        W_MTO=input_data['W_MTO'],
        W_MF=input_data['W_MF'],
        S=input_data['S'],
        C_D0=input_data['C_D0'],
        C_D2=input_data['C_D2'],
        c=input_data['c'],
        h=input_data['h'],
        V=input_data['V'],
        d=input_data['d']
    )
    assert approx_with_units(
        value_check=weight_payload,
        value_expected=output_data,
        rel=0.25
    )