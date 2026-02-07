import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.engines import calculate_corrected_tsfc
from jetfuelburn.utility.tests import approx_with_units


class TestCalculateCorrectedTSFC:
    """Test suite for calculate_corrected_tsfc."""

    def test_identity_case(self):
        """
        If actual conditions match reported conditions exactly,
        the calculated TSFC should equal the reported TSFC.
        """
        tsfc_rep = 0.6 * ureg('lb/(lbf*hr)')
        mach_rep = 0.8 * ureg.dimensionless
        alt_rep = 30000 * ureg.ft
        
        result = calculate_corrected_tsfc(
            tsfc_reported=tsfc_rep,
            M_reported=mach_rep,
            M_actual=mach_rep,
            h_reported=alt_rep,
            h_actual=alt_rep,
            beta=0.5
        )
        
        assert approx_with_units(result, tsfc_rep, rel=1e-9)

    def test_calculation_accuracy(self):
        """
        Verifies the mathematical correctness using a known manual case.
        
        Case:
        TSFC_rep = 1.0
        M_rep = 0.8, M_act = 0.4 (Ratio = 0.5)
        beta = 1.0
        h_rep = 0m (Sea Level, 288.15 K)
        h_act = 11000m (Tropopause, 216.65 K)
        
        Formula: 
        TSFC_act = 1.0 * (0.5)^1 * sqrt(216.65 / 288.15)
                 = 0.5 * sqrt(0.751865)
                 = 0.5 * 0.8671
                 ~= 0.43355
        """
        tsfc_rep = 1.0 * ureg('mg/(N*s)')
        
        result = calculate_corrected_tsfc(
            tsfc_reported=tsfc_rep,
            M_reported=0.8 * ureg.dimensionless,
            M_actual=0.4 * ureg.dimensionless,
            h_reported=0 * ureg.m,
            h_actual=11000 * ureg.m,
            beta=1.0
        )
        
        temp_ratio = 216.65 / 288.15
        expected_magnitude = 1.0 * (0.5**1.0) * (temp_ratio**0.5)
        expected = expected_magnitude * ureg('mg/(N*s)')
        
        assert approx_with_units(result, expected, rel=1e-4)

    def test_beta_units_handling(self):
        """
        Ensures 'beta' works whether passed as a float or a dimensionless Quantity.
        """
        args = {
            'tsfc_reported': 0.5 * ureg('lb/(lbf*hr)'),
            'M_reported': 0.8 * ureg.dimensionless,
            'M_actual': 0.7 * ureg.dimensionless,
            'h_reported': 30000 * ureg.ft,
            'h_actual': 30000 * ureg.ft,
        }
        
        res_float = calculate_corrected_tsfc(**args, beta=0.5)
        
        res_quant = calculate_corrected_tsfc(**args, beta=0.5 * ureg.dimensionless)
        
        assert approx_with_units(res_float, res_quant)

    @pytest.mark.parametrize("param_name, invalid_val", [
        ("tsfc_reported", -1 * ureg('lb/(lbf*hr)')),
        ("M_reported", 0 * ureg.dimensionless),
        ("M_actual", -0.5 * ureg.dimensionless),
        ("h_reported", 0 * ureg.ft), # Function strictly requires > 0, though physics allows 0
        ("h_actual", -100 * ureg.ft),
        ("beta", -0.5)
    ])
    def test_error_handling_invalid_inputs(self, param_name, invalid_val):
        """
        Checks that ValueErrors are raised for non-positive inputs 
        (according to the function's specific guards).
        """
        valid_args = {
            'tsfc_reported': 0.5 * ureg('lb/(lbf*hr)'),
            'M_reported': 0.8 * ureg.dimensionless,
            'M_actual': 0.78 * ureg.dimensionless,
            'h_reported': 35000 * ureg.ft,
            'h_actual': 30000 * ureg.ft,
            'beta': 0.5
        }
        
        valid_args[param_name] = invalid_val
        
        with pytest.raises(ValueError, match="must be > 0"):
            calculate_corrected_tsfc(**valid_args)