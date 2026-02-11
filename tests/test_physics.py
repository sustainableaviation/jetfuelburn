from pathlib import Path
import pytest
import csv
from jetfuelburn import ureg
from jetfuelburn.utility.physics import (
    _calculate_atmospheric_temperature,
    _calculate_atmospheric_density,
    _calculate_dynamic_pressure,
    _calculate_airspeed_from_mach,
    _calculate_mach_from_airspeed,
    _calculate_speed_of_sound,
)

from jetfuelburn.utility.tests import approx_with_units


def load_isa_csv():
    r"""
    Helper function to load a CSV file containing
    parameters of the International Standard Atmosphere (ISA).
    Returns a list of dictionaries where values are float-converted.

    References
    ----------
    "International Standard Atmosphere (ISA) Table" in Young, T. M. (2017).
    _Performance of the Jet Transport Airplane: Analysis Methods, Flight Operations, and Regulations._
    John Wiley & Sons.
    doi:[10.1002/9781118534786.app1](https://doi.org/10.1002/9781118534786.app1)

    See Also
    --------
    [International Standard Atmosphere (ISA) entry on Wikipedia](https://en.wikipedia.org/wiki/International_Standard_Atmosphere)

    Returns
    -------
    List[Dict[str, float]]
        A list of dictionaries with ISA parameters, where each dictionary corresponds to a row in the CSV file.
        Of the form:
        ```
        [
            {
                'H_ft': 0.0,
                'H_m': 0.0,
                'theta': 1.0,
                'T_K': 288.15,
                'T_C': 15.0,
                'delta': 1.0,
                'P_N/m^2': 101325.0,
                'P_lb/ft^2': 2116.21,
                'sigma': 1.0,
                'rho_kg/m^3': 1.225,
                'rho_slug/ft^3': 0.002377,
                'a_m/s': 340.3,
                'a_ft/s': 1116.0,
                'a_kt': 661.5
            },
            ...
        ]
        ```
    """
    csv_path = Path(__file__).parent / "data" / "isa.csv"
    data = []
    with open(csv_path, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k: float(v) for k, v in row.items()}
            data.append(clean_row)
    return data


ISA_DATA = load_isa_csv()


class TestCalculateAtmosphericTemperature:
    """Test suite for _calculate_atmospheric_temperature."""

    @pytest.mark.parametrize("row", ISA_DATA)
    def test_values_against_isa_table(self, row):
        """Checks if calculated temperature matches the ISA table values."""
        altitude = row["H_m"] * ureg.meter
        expected = ureg.Quantity(row["T_C"], ureg.degC)
        result = _calculate_atmospheric_temperature(altitude)

        assert approx_with_units(result, expected, abs=0.1)

    def test_output_units(self):
        """Checks that the function returns degrees Celsius."""
        result = _calculate_atmospheric_temperature(0 * ureg.meter)
        assert result.units == ureg.degC

    def test_error_handling(self):
        """Checks that out-of-bounds altitudes raise ValueError."""
        with pytest.raises(ValueError, match="Altitude must not be"):
            _calculate_atmospheric_temperature(-1 * ureg.meter)
        with pytest.raises(ValueError, match="Altitude must not be"):
            _calculate_atmospheric_temperature(20001 * ureg.meter)


class TestCalculateAtmosphericDensity:
    """Test suite for _calculate_atmospheric_density."""

    @pytest.mark.parametrize("row", ISA_DATA)
    def test_values_against_isa_table(self, row):
        """Checks if calculated density matches the ISA table values."""
        altitude = row["H_m"] * ureg.meter
        expected = row["rho_kg/m^3"] * (ureg.kg / ureg.m**3)
        result = _calculate_atmospheric_density(altitude)

        assert approx_with_units(result, expected, rel=1e-2)

    def test_output_units(self):
        """Checks that the function returns kg/m³."""
        result = _calculate_atmospheric_density(0 * ureg.meter)
        assert result.units == ureg.kg / ureg.m**3

    def test_error_handling(self):
        """Checks that out-of-bounds altitudes raise ValueError."""
        with pytest.raises(ValueError, match="Altitude must not be"):
            _calculate_atmospheric_density(-0.1 * ureg.meter)
        with pytest.raises(ValueError, match="Altitude must not be"):
            _calculate_atmospheric_density(20000.1 * ureg.meter)


class TestCalculateSpeedOfSound:
    """Test suite for _calculate_speed_of_sound."""

    @pytest.mark.parametrize("row", ISA_DATA)
    def test_values_against_isa_table(self, row):
        """Checks if speed of sound matches ISA table for the given temperature."""
        temperature = ureg.Quantity(row["T_C"], ureg.degC)
        expected = (ureg.Quantity(row["a_kt"], ureg.knot)).to(ureg.kph)
        result = _calculate_speed_of_sound(temperature)

        assert approx_with_units(result, expected, rel=1e-3)

    def test_output_units(self):
        """Checks that the function returns speed units (kph)."""
        input_temp = ureg.Quantity(15, ureg.degC)
        result = _calculate_speed_of_sound(input_temp)
        assert result.units == ureg.kph

    def test_error_handling(self):
        """Checks that absolute zero temperatures raise ValueError."""
        invalid_temp = ureg.Quantity(-274, ureg.degC)
        with pytest.raises(ValueError, match="absolute zero"):
            _calculate_speed_of_sound(invalid_temp)


class TestCalculateAircraftVelocity:
    """Test suite for _calculate_airspeed_from_mach."""

    @pytest.mark.parametrize("row", ISA_DATA)
    def test_values_against_isa_table(self, row):
        """
        Validates velocity calculation.
        At Mach 1.0, the velocity must equal the local speed of sound from the table.
        """
        altitude = row["H_m"] * ureg.meter
        mach = 1.0
        expected = (row["a_kt"] * ureg.knot).to(ureg.kph)

        result = _calculate_airspeed_from_mach(mach, altitude)

        assert approx_with_units(result, expected, rel=1e-3)

    def test_output_units(self):
        """Checks that the function returns speed units (kph)."""
        result = _calculate_airspeed_from_mach(0.8, 10000 * ureg.meter)
        assert result.units == ureg.kph

    def test_error_handling(self):
        """Checks that invalid inputs raise errors (propagated from atmospheric functions)."""
        with pytest.raises(ValueError):
            _calculate_airspeed_from_mach(0.8, -500 * ureg.meter)


class TestCalculateDynamicPressure:
    """Test suite for _calculate_dynamic_pressure."""

    def test_output_units(self):
        """Checks that the function returns pressure units (Pascals)."""
        result = _calculate_dynamic_pressure(100 * ureg.kph, 1000 * ureg.meter)
        assert result.units == ureg.pascal

    def test_error_handling(self):
        """Checks that invalid altitude inputs raise ValueError."""
        with pytest.raises(ValueError):
            _calculate_dynamic_pressure(500 * ureg.kph, 25000 * ureg.meter)

    def test_calculation_accuracy(self):
        """
        Verifies the math: q = 0.5 * rho * v^2
        Using Sea Level standard conditions:
        rho = 1.225 kg/m^3
        v = 100 m/s
        q = 0.5 * 1.225 * 10000 = 6125 Pa
        """
        altitude = 0 * ureg.meter
        speed = 100 * ureg.mps
        expected = 6125 * ureg.Pa

        result = _calculate_dynamic_pressure(speed, altitude)

        assert approx_with_units(result, expected, rel=1e-3)


class TestCalculateMachFromAirspeed:
    """Test suite for _calculate_mach_from_airspeed."""

    @pytest.mark.parametrize("row", ISA_DATA)
    def test_mach_one_equivalence(self, row):
        """
        At Mach 1.0, True Airspeed (TAS) equals the local Speed of Sound.
        We input the speed of sound from the ISA table and expect Mach 1.0 back.
        """
        altitude = row["H_m"] * ureg.meter
        # Input speed is the local speed of sound
        airspeed = (row["a_kt"] * ureg.knot).to(ureg.kph)

        expected_mach = 1.0 * ureg.dimensionless

        result = _calculate_mach_from_airspeed(airspeed, altitude)

        assert approx_with_units(result, expected_mach, rel=1e-3)

    def test_round_trip_conversion(self):
        """
        Checks consistency between the two Mach functions:
        Mach -> Airspeed -> Mach should return the original value.
        """
        original_mach = 0.82
        altitude = 10500 * ureg.meter

        airspeed = _calculate_airspeed_from_mach(original_mach, altitude)
        result_mach = _calculate_mach_from_airspeed(airspeed, altitude)

        assert result_mach.units == ureg.dimensionless
        assert approx_with_units(
            result_mach, original_mach * ureg.dimensionless, rel=1e-5
        )

    def test_output_units(self):
        """Checks that the function returns a dimensionless Quantity."""
        result = _calculate_mach_from_airspeed(
            airspeed=500 * ureg.kph, altitude=5000 * ureg.m
        )
        assert result.units == ureg.dimensionless

    def test_error_handling(self):
        """Checks that altitude errors propagate correctly."""
        with pytest.raises(ValueError):
            _calculate_mach_from_airspeed(500 * ureg.kph, 25000 * ureg.m)
