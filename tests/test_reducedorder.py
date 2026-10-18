import re
import pytest
from pint import DimensionalityError
import jetfuelburn.reducedorder
from jetfuelburn import ureg
from .helpers import approx_with_units
from jetfuelburn.reducedorder import (
    yanto_etal,
    aim2015,
    seymour_etal,
    lee_etal,
    eea_emission_inventory_2009,
    myclimate,
    sacchi_etal,
    montlaur_etal,
    gossling_etal,
    turgut_etal,
    models_for_aircraft,
)
from .fixtures.reducedorder import (
    fixture_yanto_B739,
    fixture_aim2015_B787,
    fixture_seymour_B738,
    fixture_lee_B732,
    fixture_eea_A320,
    fixture_myclimate_standard,
    fixture_myclimate_aircraft,
    fixture_gossling_gulfstream5,
    fixture_turgut_cruise,
)


@pytest.mark.parametrize(
    "distance_km, seats, expected_fuel_ask, description",
    [
        # --- Model D, E (Small) Cases ---
        (1500, 150, 19.98, "Typical Small Aircraft"),
        (100, 50, 93.93, "Minimum Bounds Small"),
        (4000, 100, 23.35, "Long Range Small"),
        # --- Model B, D (Large) Cases ---
        # Formula: 0.7361 + 6651/D + 5.989e-4*D + 6.152e-2*S - 1.014e-6*D*S
        (3000, 200, 16.45, "Typical Large Aircraft"),
        (12000, 350, 25.75, "Max Range Large"),
        # --- Boundary / Edge Cases ---
        (200, 172, 44.66, "Exact Boundary for Large Model (Min Dist/Min Seats)"),
        (5000, 171, 18.30, "Max Dist for Small Model"),
    ],
)
def test_value_consistency(distance_km, seats, expected_fuel_ask, description):
    """
    Verifies that the new class-based implementation matches the
    original reference values.

    All expected values were calculated using the reference implementation:
    https://github.com/luis-uow/emissions_fuel_estimation?tab=GPL-3.0-1-ov-file
    """
    # 1. Calculate New Implementation Value
    new_result = montlaur_etal.calculate(
        distance=distance_km * ureg.km, available_seats=seats
    )


def test_unit_consistency():
    result = montlaur_etal.calculate(1000 * ureg.km, 150)
    assert result.check("[mass]/[length]")


def test_invalid_input_raising():
    with pytest.raises(ValueError):
        montlaur_etal.calculate(50000 * ureg.km, 200)


class TestSacchiEtal:

    def test_input_validation(self):
        """Test that invalid years and passenger counts raise correct errors."""

        # 1. Year < 2018
        with pytest.raises(ValueError, match="Year must be 2018 or later"):
            sacchi_etal.calculate(year=2017, pax_max=180, pax=150, R=1000 * ureg.km)

        # 2. Pax > Pax Max
        with pytest.raises(ValueError, match="between 0 and maximum pax"):
            sacchi_etal.calculate(year=2020, pax_max=180, pax=181, R=1000 * ureg.km)

        # 3. Negative Pax
        with pytest.raises(ValueError, match="between 0 and maximum pax"):
            sacchi_etal.calculate(year=2020, pax_max=180, pax=-1, R=1000 * ureg.km)

    def test_dimensionality_checks(self):
        """Test that passing wrong units raises DimensionalityError."""

        # 1. Range with Mass Units
        with pytest.raises(DimensionalityError):
            sacchi_etal.calculate(
                year=2020, pax_max=180, pax=150, R=1000 * ureg.kg  # Wrong dimension
            )

        # 2. Tolerance with Time units
        with pytest.raises(DimensionalityError):
            sacchi_etal.calculate(
                year=2020,
                pax_max=180,
                pax=150,
                R=1000 * ureg.km,
                tolerance=50 * ureg.second,  # Wrong dimension
            )

    def test_unit_conversion_consistency(self):
        """Test that the function handles unit conversion (nmi to km) correctly."""
        year = 2025
        pax_max = 180
        pax = 150

        # Calculate with km
        res_km = sacchi_etal.calculate(
            year=year, pax_max=pax_max, pax=pax, R=1000 * ureg.km
        )

        # Calculate with nmi (approx 539.957 nmi = 1000 km)
        res_nmi = sacchi_etal.calculate(
            year=year, pax_max=pax_max, pax=pax, R=539.9568 * ureg.nmi
        )

        # Ensure results are practically identical
        assert approx_with_units(res_km, res_nmi, rel=1e-5)

    def test_manual_verification_cases(self):
        """
        Verifies model output against known calculated values for specific scenarios.
        """

        # Case 1: 2018
        # See: Cell AE8 in sheet "Scenarios" of Supplement 1 to Sacchi et al. (2023)
        # https://doi.org/10.5281/zenodo.8059750
        fuel_1 = sacchi_etal.calculate(
            year=2018, pax_max=210, pax=177, R=6654 * ureg.km
        )
        expected_1 = 42278 * ureg.kg
        print(f"Case 1 (2018, 6654km): Got {fuel_1:.1f}, Expected {expected_1:.1f}")

        assert approx_with_units(
            value_check=fuel_1, value_expected=expected_1, rel=0.025
        )

        # Case 2: 2025
        # See: Cell AE15 in sheet "Scenarios" of Supplement 1 to Sacchi et al. (2023)
        # https://doi.org/10.5281/zenodo.8059750
        fuel_2 = sacchi_etal.calculate(
            year=2025, pax_max=214, pax=184, R=6654 * ureg.km
        )
        expected_2 = 39606 * ureg.kg
        print(f"Case 2 (2025, 6654km): Got {fuel_2:.1f}, Expected {expected_2:.1f}")

        assert approx_with_units(
            value_check=fuel_2, value_expected=expected_2, rel=0.025
        )

        # Case 2: 2025
        # See: Cell AE15 in sheet "Scenarios" of Supplement 1 to Sacchi et al. (2023)
        # https://doi.org/10.5281/zenodo.8059750
        fuel_3 = sacchi_etal.calculate(
            year=2050, pax_max=231, pax=214, R=6654 * ureg.km
        )
        expected_3 = 31854 * ureg.kg
        print(f"Case 3 (2050, 6654km): Got {fuel_3:.1f}, Expected {expected_3:.1f}")

        assert approx_with_units(
            value_check=fuel_3, value_expected=expected_3, rel=0.025
        )


def test_yanto_etal_B739(fixture_yanto_B739):
    make_case, params = fixture_yanto_B739

    for r, pl in params:
        input_data, expected_output = make_case(r, pl)
        calculated_output = yanto_etal.calculate(
            acft=input_data["acft"],
            R=input_data["R"],
            PL=input_data["PL"],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to("kg"),
            rel=0.075,
        )


def test_aim2015(fixture_aim2015_B787):
    make_case, distances = fixture_aim2015_B787

    for d in distances:
        input_data, expected_output = make_case(d)
        calculated_output = aim2015.calculate(
            acft_size_class=input_data["acft_size_class"],
            D_climb=input_data["D_climb"],
            D_cruise=input_data["D_cruise"],
            D_descent=input_data["D_descent"],
            PL=input_data["PL"],
        )
        assert approx_with_units(
            value_check=sum(calculated_output.values()),
            value_expected=expected_output.to("kg"),
            rel=0.075,
        )


def test_seymour(fixture_seymour_B738):
    make_case, ranges = fixture_seymour_B738

    for R in ranges:
        input_data, expected_output = make_case(R)
        calculated_output = seymour_etal.calculate(
            acft=input_data["acft"],
            R=input_data["R"],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to("kg"),
            rel=1e-6,
        )


def test_seymour_outside_fitted_range():
    # D228: a1 < 0 and a maximum range of 500 km (Table L.6). The fit drops below zero at about 1,613 km.
    assert seymour_etal.calculate(acft="D228", R=500 * ureg.km) > 0 * ureg.kg
    with pytest.raises(ValueError, match="outside its fitted range"):
        seymour_etal.calculate(acft="D228", R=2000 * ureg.km)
    with pytest.raises(ValueError, match="must be non-negative"):
        seymour_etal.calculate(acft="B738", R=-1 * ureg.km)


def test_eea2009(fixture_eea_A320):
    make_case, ranges = fixture_eea_A320

    for R in ranges:
        input_data, expected_output = make_case(R)
        calculated_output = eea_emission_inventory_2009.calculate(
            acft=input_data["acft"],
            R=input_data["R"],
        )
        assert approx_with_units(
            value_check=calculated_output["mass_fuel_total"].to("kg"),
            value_expected=expected_output.to("kg"),
            rel=0.075,
        )


def test_myclimate_standard(fixture_myclimate_standard):
    make_case, params = fixture_myclimate_standard

    for x in params:
        input_data, expected_output = make_case(x)
        calculated_output = myclimate.calculate(
            acft=input_data["acft"],
            x=input_data["x"],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to("kg"),
            rel=0.075,
        )


def test_myclimate_aircraft(fixture_myclimate_aircraft):
    make_case, params = fixture_myclimate_aircraft

    for acft, x in params:
        input_data, expected_output = make_case(acft, x)
        calculated_output = myclimate.calculate(
            acft=input_data["acft"],
            x=input_data["x"],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to("kg"),
            rel=1e-9,
        )


def test_gossling_gulfstream5(fixture_gossling_gulfstream5):
    make_case, params = fixture_gossling_gulfstream5

    for t in params:
        input_data, expected_output = make_case(t)
        calculated_output = gossling_etal.calculate(
            acft=input_data["acft"],
            flight_time=input_data["flight_time"],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to("kg"),
            rel=1e-9,
        )


def test_gossling_consumption_range_matches_paper():
    """
    The abstract of Gössling et al. (2024) states that the identified private-jet models have
    a fuel consumption ranging between 48 and 576 gallons per hour.
    """
    fuel_flows = gossling_etal._fuel_flow_gph.values()
    assert min(fuel_flows) == 48
    assert max(fuel_flows) == 576


def test_gossling_model_count():
    """
    Guards the aircraft count documented in the class docstring against silent changes
    to the bundled `data/Gossling2024/models.csv` dataset or its `icao.csv` mapping.
    """
    assert len(gossling_etal.list_aircraft()) == 69


def test_gossling_icao_mapping():
    """
    Every model of the dataset appears in `icao.csv`, and every aircraft key is an ICAO designator.
    """
    import csv
    from importlib import resources

    package = "jetfuelburn.data.Gossling2024"
    with resources.open_text(package, "models.csv") as file:
        models = {row["model"] for row in csv.DictReader(file)}
    with resources.open_text(package, "icao.csv") as file:
        mapping = {row["model"]: row["icao"] for row in csv.DictReader(file)}
    assert set(mapping) == models
    assert all(
        re.fullmatch(r"[A-Z][A-Z0-9]{1,3}", a) for a in gossling_etal.list_aircraft()
    )
    assert "GULFSTREAM 5" not in gossling_etal.list_aircraft()


def test_turgut_cruise(fixture_turgut_cruise):
    make_case, params = fixture_turgut_cruise

    for key in params:
        input_data, expected_output = make_case(key)
        calculated_output = turgut_etal.calculate(
            acft=input_data["acft"],
            altitude=input_data["altitude"],
            mass=input_data["mass"],
            TAS=input_data["TAS"],
        )
        assert approx_with_units(
            value_check=calculated_output.to("kg/hour"),
            value_expected=expected_output.to("kg/hour"),
            rel=1e-9,
        )


def test_turgut_below_optimum_altitude_matches_paper():
    """
    Section 4 of Turgut et al. (2014) states that, for the B738 at the mean cruise conditions
    (35,000 ft, 60.3 tonne, 364 knot), cruising 2000/4000/8000 ft below the optimum altitude
    increases hourly fuel consumption by 2.3%/4.6%/9.1%, respectively.
    """
    mass = 60.3 * ureg.metric_ton
    tas = 364 * ureg.knot
    ff_optimum = turgut_etal.calculate(
        acft="B738", altitude=35000 * ureg.ft, mass=mass, TAS=tas
    )
    for delta_ft, expected_increase in ((2000, 0.023), (4000, 0.046), (8000, 0.091)):
        ff_below = turgut_etal.calculate(
            acft="B738", altitude=(35000 - delta_ft) * ureg.ft, mass=mass, TAS=tas
        )
        increase = (ff_below - ff_optimum) / ff_optimum
        assert increase.magnitude == pytest.approx(expected_increase, abs=0.001)


def test_turgut_returns_rate():
    result = turgut_etal.calculate(
        acft="A320",
        altitude=35000 * ureg.ft,
        mass=60 * ureg.metric_ton,
        TAS=370 * ureg.knot,
    )
    assert result.check("[mass]/[time]")


def test_turgut_invalid_input_raising():
    base = dict(
        altitude=35000 * ureg.ft, mass=60 * ureg.metric_ton, TAS=364 * ureg.knot
    )
    with pytest.raises(ValueError):
        turgut_etal.calculate(acft="NOT A MODEL", **base)
    with pytest.raises(ValueError):
        turgut_etal.calculate(
            acft="B738",
            altitude=-1 * ureg.ft,
            mass=60 * ureg.metric_ton,
            TAS=364 * ureg.knot,
        )
    with pytest.raises(ValueError):
        turgut_etal.calculate(
            acft="B738", altitude=35000 * ureg.ft, mass=0 * ureg.kg, TAS=364 * ureg.knot
        )
    with pytest.raises(ValueError):
        turgut_etal.calculate(
            acft="B738",
            altitude=35000 * ureg.ft,
            mass=60 * ureg.metric_ton,
            TAS=-5 * ureg.knot,
        )


def test_turgut_dimensionality_checks():
    with pytest.raises(DimensionalityError):
        turgut_etal.calculate(
            acft="B738",
            altitude=35000 * ureg.kg,  # Wrong dimension
            mass=60 * ureg.metric_ton,
            TAS=364 * ureg.knot,
        )


def test_models_for_aircraft():
    # A320 is an exact key in several ICAO-designator-keyed models
    result = models_for_aircraft("A320")
    assert result == sorted(result)  # sorted output
    for expected in ("yanto_etal", "seymour_etal", "turgut_etal", "aim2015"):
        assert expected in result
    # each returned model must genuinely list the aircraft
    for name in result:
        model = getattr(jetfuelburn.reducedorder, name)
        assert "A320" in model.list_aircraft()

    # an ICAO designator listed by one model only, and one listed by several
    assert models_for_aircraft("C25M") == ["gossling_etal"]
    assert models_for_aircraft("GLF5") == ["gossling_etal", "seymour_etal"]
    assert models_for_aircraft("Overall") == ["turgut_etal"]

    # models without an list_aircraft() method are never included
    assert "montlaur_etal" not in models_for_aircraft("A320")
    assert "sacchi_etal" not in models_for_aircraft("A320")

    # matching is exact: unknown / wrong-case aircraft return an empty list
    assert models_for_aircraft("a320") == []
    assert models_for_aircraft("NOT AN AIRCRAFT") == []


def test_gossling_unit_consistency():
    result = gossling_etal.calculate(acft="GLF5", flight_time=2 * ureg.hour)
    assert result.check("[mass]")


def test_gossling_invalid_input_raising():
    with pytest.raises(ValueError):
        gossling_etal.calculate(acft="NOT AN AIRCRAFT", flight_time=1 * ureg.hour)
    with pytest.raises(ValueError):
        gossling_etal.calculate(acft="GULFSTREAM 5", flight_time=1 * ureg.hour)
    with pytest.raises(ValueError):
        gossling_etal.calculate(acft="GLF5", flight_time=-1 * ureg.hour)


def test_gossling_dimensionality_checks():
    with pytest.raises(DimensionalityError):
        gossling_etal.calculate(
            acft="GLF5", flight_time=100 * ureg.km  # Wrong dimension
        )
