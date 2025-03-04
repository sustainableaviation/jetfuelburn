# %%
import pytest
import pandas as pd
import numpy as np
import pint
import pint_pandas
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

@pytest.fixture
def climb_segment_1() -> tuple[pd.DataFrame, dict]:
    """
    Generate fixtures for testing _generate_eurocontrol_climb_segments_complete.
    
    Generates a Pandas Series containing aircraft performance parameters, where:
    `alt_ceiling_cruise` < 24'000 ft
    and
    `rate_mach` is NaN

    See Also
    --------
    _generate_eurocontrol_climb_segments_complete

    Returns
    -------
    tuple[pd.DataFrame, dict]
        Input data and expected output data for testing _generate_eurocontrol_climb_segments_complete.
        
    """
    alt_ceiling_cruise = 22000
    rate_initial = 1000
    rate_5000_15000 = 1500
    rate_15000_24000 = 1200
    rate_mach = np.nan
    v_ground_initial = 250
    v_ground_5000_15000 = 300
    v_ground_15000_24000 = 350
    v_ground_mach = np.nan

    input_data = pd.DataFrame(
        {
            "alt_ceiling_cruise": pd.Series([alt_ceiling_cruise], dtype="pint[ft][float]"),
            "rate_initial": pd.Series([rate_initial], dtype="pint[ft/min][float]"),
            "rate_5000_15000": pd.Series([rate_5000_15000], dtype="pint[ft/min][float]"),
            "rate_15000_24000": pd.Series([rate_15000_24000], dtype="pint[ft/min][float]"),
            "rate_mach": pd.Series([rate_mach], dtype="pint[ft/min][float]"),
            "v_ground_initial": pd.Series([v_ground_initial], dtype="pint[kts][float]"),
            "v_ground_5000_15000": pd.Series([v_ground_5000_15000], dtype="pint[kts][float]"),
            "v_ground_15000_24000": pd.Series([v_ground_15000_24000], dtype="pint[kts][float]"),
            "v_ground_mach": pd.Series([v_ground_mach], dtype="pint[ft/min][float]"),
        }
    ).iloc[0]

    output_data_correct: dict = {
        "initial": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 5000 * ureg.ft,
            'rate': rate_initial * (ureg.ft / ureg.min),
            'v_ground': v_ground_initial * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "5000_15000": {
            'alt_bottom': 5000 * ureg.ft,
            'alt_top': 15000 * ureg.ft,
            'rate': rate_5000_15000 * (ureg.ft / ureg.min),
            'v_ground': v_ground_5000_15000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "15000_24000": {
            'alt_bottom': 15000 * ureg.ft,
            'alt_top': alt_ceiling_cruise * ureg.ft,
            'rate': rate_15000_24000 * (ureg.ft / ureg.min),
            'v_ground': v_ground_15000_24000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
    }

    return input_data, output_data_correct


@pytest.fixture
def climb_segment_2() -> tuple[pd.DataFrame, dict]:
    """
    Generate fixtures for testing _generate_eurocontrol_climb_segments_complete.
    
    Generates a Pandas Series containing aircraft performance parameters, where:
    `alt_ceiling_cruise` > 24'000 ft

    See Also
    --------
    _generate_eurocontrol_climb_segments_complete

    Returns
    -------
    tuple[pd.DataFrame, dict]
        Input data and expected output data for testing _generate_eurocontrol_climb_segments_complete.
        
    """
    alt_ceiling_cruise = 32000
    rate_initial = 1000
    rate_5000_15000 = 1500
    rate_15000_24000 = 1200
    rate_mach = 1000
    v_ground_initial = 250
    v_ground_5000_15000 = 300
    v_ground_15000_24000 = 350
    v_ground_mach = 600

    input_data = pd.DataFrame(
        {
            "alt_ceiling_cruise": pd.Series([alt_ceiling_cruise], dtype="pint[ft][float]"),
            "rate_initial": pd.Series([rate_initial], dtype="pint[ft/min][float]"),
            "rate_5000_15000": pd.Series([rate_5000_15000], dtype="pint[ft/min][float]"),
            "rate_15000_24000": pd.Series([rate_15000_24000], dtype="pint[ft/min][float]"),
            "rate_mach": pd.Series([rate_mach], dtype="pint[ft/min][float]"),
            "v_ground_initial": pd.Series([v_ground_initial], dtype="pint[kts][float]"),
            "v_ground_5000_15000": pd.Series([v_ground_5000_15000], dtype="pint[kts][float]"),
            "v_ground_15000_24000": pd.Series([v_ground_15000_24000], dtype="pint[kts][float]"),
            "v_ground_mach": pd.Series([v_ground_mach], dtype="pint[kts][float]"),
        }
    ).iloc[0]

    output_data_correct: dict = {
        "initial": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 5000 * ureg.ft,
            'rate': rate_initial * (ureg.ft / ureg.min),
            'v_ground': v_ground_initial * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "5000_15000": {
            'alt_bottom': 5000 * ureg.ft,
            'alt_top': 15000 * ureg.ft,
            'rate': rate_5000_15000 * (ureg.ft / ureg.min),
            'v_ground': v_ground_5000_15000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "15000_24000": {
            'alt_bottom': 15000 * ureg.ft,
            'alt_top': 24000 * ureg.ft,
            'rate': rate_15000_24000 * (ureg.ft / ureg.min),
            'v_ground': v_ground_15000_24000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "mach": {
            'alt_bottom': 24000 * ureg.ft,
            'alt_top': alt_ceiling_cruise * ureg.ft,
            'rate': rate_mach * (ureg.ft / ureg.min),
            'v_ground': v_ground_mach * ureg.kts,
            'time': 0,
            'distance': 0,
        },
    }

    return input_data, output_data_correct


@pytest.fixture
def descent_segment_1() -> tuple[pd.DataFrame, dict]:
    """
    Generate fixtures for testing _generate_eurocontrol_descent_segments_complete.
    
    Generates a Pandas Series containing aircraft performance parameters, where:
    `alt_ceiling_cruise` < 24'000 ft

    See Also
    --------
    _generate_eurocontrol_descent_segments_complete

    Returns
    -------
    tuple[pd.DataFrame, dict]
        Input data and expected output data for testing _generate_eurocontrol_descent_segments_complete.
        
    """
    alt_ceiling_cruise = 20000
    rate_approach = 500
    rate_24000_to_10000 = 1500
    rate_cruise_to_24000 = np.nan
    v_approach = 200
    v_24000_to_10000 = 400
    v_cruise_to_24000 = np.nan

    input_data = pd.DataFrame(
        {
            "alt_ceiling_cruise": pd.Series([alt_ceiling_cruise], dtype="pint[ft][float]"),
            "rate_approach": pd.Series([rate_approach], dtype="pint[ft/min][float]"),
            "rate_24000_to_10000": pd.Series([rate_24000_to_10000], dtype="pint[ft/min][float]"),
            "rate_cruise_to_24000": pd.Series([rate_cruise_to_24000], dtype="pint[ft/min][float]"),
            "v_approach": pd.Series([v_approach], dtype="pint[kts][float]"),
            "v_24000_to_10000": pd.Series([v_24000_to_10000], dtype="pint[kts][float]"),
            "v_cruise_to_24000": pd.Series([v_cruise_to_24000], dtype="pint[kts][float]"),
        }
    ).iloc[0]

    output_data_correct: dict = {
        "approach": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 10000 * ureg.ft,
            'rate': rate_approach * (ureg.ft / ureg.min),
            'v_ground': v_approach * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "24000_to_10000": {
            'alt_bottom': 10000 * ureg.ft,
            'alt_top': alt_ceiling_cruise * ureg.ft,
            'rate': rate_24000_to_10000 * (ureg.ft / ureg.min),
            'v_ground': v_24000_to_10000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
    }

    return input_data, output_data_correct


@pytest.fixture
def descent_segment_2() -> tuple[pd.DataFrame, dict]:
    """
    Generate fixtures for testing _generate_eurocontrol_descent_segments_complete.
    
    Generates a Pandas Series containing aircraft performance parameters, where:
    `alt_ceiling_cruise` > 24'000 ft

    See Also
    --------
    _generate_eurocontrol_descent_segments_complete

    Returns
    -------
    tuple[pd.DataFrame, dict]
        Input data and expected output data for testing _generate_eurocontrol_descent_segments_complete.
        
    """
    alt_ceiling_cruise = 32000
    rate_approach = 500
    rate_24000_to_10000 = 1500
    rate_cruise_to_24000 = 1000
    v_approach = 200
    v_24000_to_10000 = 400
    v_cruise_to_24000 = 500

    input_data = pd.DataFrame(
        {
            "alt_ceiling_cruise": pd.Series([alt_ceiling_cruise], dtype="pint[ft][float]"),
            "rate_approach": pd.Series([rate_approach], dtype="pint[ft/min][float]"),
            "rate_24000_to_10000": pd.Series([rate_24000_to_10000], dtype="pint[ft/min][float]"),
            "rate_cruise_to_24000": pd.Series([rate_cruise_to_24000], dtype="pint[ft/min][float]"),
            "v_approach": pd.Series([v_approach], dtype="pint[kts][float]"),
            "v_24000_to_10000": pd.Series([v_24000_to_10000], dtype="pint[kts][float]"),
            "v_cruise_to_24000": pd.Series([v_cruise_to_24000], dtype="pint[kts][float]"),
        }
    ).iloc[0]

    output_data_correct: dict = {
        "approach": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 10000 * ureg.ft,
            'rate': rate_approach * (ureg.ft / ureg.min),
            'v_ground': v_approach * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "24000_to_10000": {
            'alt_bottom': 10000 * ureg.ft,
            'alt_top': 24000 * ureg.ft,
            'rate': rate_24000_to_10000 * (ureg.ft / ureg.min),
            'v_ground': v_24000_to_10000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
        "cruise_to_24000": {
            'alt_bottom': 24000 * ureg.ft,
            'alt_top': alt_ceiling_cruise * ureg.ft,
            'rate': rate_cruise_to_24000 * (ureg.ft / ureg.min),
            'v_ground': v_cruise_to_24000 * ureg.kts,
            'time': 0,
            'distance': 0,
        },
    }

    return input_data, output_data_correct


@pytest.fixture
def distance_and_time_based_on_alt_cruise_1() -> tuple[dict, dict]:
    input_data = {
        'alt_cruise': 32000 * ureg.ft,
        'segments': {
            "approach": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 10000 * ureg.ft,
                'rate': 500 * (ureg.ft / ureg.min),
                'v_ground': 200 * ureg.kts,
                'time': 0,
                'distance': 0,
            },
            "24000_to_10000": {
                'alt_bottom': 10000 * ureg.ft,
                'alt_top': 24000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 400 * ureg.kts,
                'time': 0,
                'distance': 0,
            },
            "cruise_to_24000": {
                'alt_bottom': 24000 * ureg.ft,
                'alt_top': 32000 * ureg.ft,
                'rate': 1000 * (ureg.ft / ureg.min),
                'v_ground': 500 * ureg.kts,
                'time': 0,
                'distance': 0,
            },
        }
    }
    output_data_correct = {
        "approach": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 10000 * ureg.ft,
            'rate': 500 * (ureg.ft / ureg.min),
            'v_ground': 200 * ureg.kts,
            'time': (10000/500) * ureg.min,
            'distance': ((10000/500) * ureg.min * 200 * ureg.kts).to(ureg.km),
        },
        "24000_to_10000": {
            'alt_bottom': 10000 * ureg.ft,
            'alt_top': 24000 * ureg.ft,
            'rate': 1500 * (ureg.ft / ureg.min),
            'v_ground': 400 * ureg.kts,
            'time': (14000/1500) * ureg.min,
            'distance': ((14000/1500) * ureg.min * 400 * ureg.kts).to(ureg.km),
        },
        "cruise_to_24000": {
            'alt_bottom': 24000 * ureg.ft,
            'alt_top': 32000 * ureg.ft,
            'rate': 1000 * (ureg.ft / ureg.min),
            'v_ground': 500 * ureg.kts,
            'time': ((32000-24000)/1000) * ureg.min,
            'distance': (8 * ureg.min * 500 * ureg.kts).to(ureg.km),
        },
    }
    return input_data, output_data_correct


@pytest.fixture
def distance_and_time_based_on_alt_cruise_2() -> tuple[dict, dict]:
    input_data = {
        'alt_cruise': 20000 * ureg.ft,
        'segments': {
            "initial": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 5000 * ureg.ft,
                'rate': 2000 * (ureg.ft / ureg.min),
                'v_ground': 250 * ureg.kts,
                'time': 0,
                'distance': 0,
                },
            "5000_15000": {
                'alt_bottom': 5000 * ureg.ft,
                'alt_top': 15000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 350 * ureg.kts,
                'time': 0,
                'distance': 0,
            },
            "15000_24000": {
                'alt_bottom': 15000 * ureg.ft,
                'alt_top': 24000 * ureg.ft,
                'rate': 1000 * (ureg.ft / ureg.min),
                'v_ground': 450 * ureg.kts,
                'time': 0,
                'distance': 0,
            },
            "mach": {
                'alt_bottom': 24000 * ureg.ft,
                'alt_top': 32000 * ureg.ft,
                'rate': 1000 * (ureg.ft / ureg.min),
                'v_ground': 500 * ureg.kts,
                'time': 0,
                'distance': 0,
            },
        }
    }
    output_data_correct = {
        "initial": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 5000 * ureg.ft,
            'rate': 2000 * (ureg.ft / ureg.min),
            'v_ground': 250 * ureg.kts,
            'time': (5000/2000) * ureg.min,
            'distance': ((5000/2000) * ureg.min * 250 * ureg.kts).to(ureg.km),
            },
        "5000_15000": {
            'alt_bottom': 5000 * ureg.ft,
            'alt_top': 15000 * ureg.ft,
            'rate': 1500 * (ureg.ft / ureg.min),
            'v_ground': 350 * ureg.kts,
            'time': (10000/1500) * ureg.min,
            'distance': ((10000/1500) * ureg.min * 350 * ureg.kts).to(ureg.km),
        },
        "15000_24000": {
            'alt_bottom': 15000 * ureg.ft,
            'alt_top': 20000 * ureg.ft,
            'rate': 1000 * (ureg.ft / ureg.min),
            'v_ground': 450 * ureg.kts,
            'time': ((20000-15000)/1000) * ureg.min,
            'distance': (5 * ureg.min * 450 * ureg.kts).to(ureg.km),
        },
    }
    return input_data, output_data_correct


@pytest.fixture
def distance_and_time_based_on_distance_1() -> tuple[dict, dict]:
    input_data = {
        'distance_traveled': 100 * ureg.km,
        'segments': {
            "initial": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 5000 * ureg.ft,
                'rate': 2000 * (ureg.ft / ureg.min),
                'v_ground': 250 * ureg.kts,
                'time': (5000/2000) * ureg.min,
                'distance': ((5000/2000) * ureg.min * 250 * ureg.kts).to(ureg.km),
            },
            "5000_15000": {
                'alt_bottom': 5000 * ureg.ft,
                'alt_top': 15000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 350 * ureg.kts,
                'time': (10000/1500) * ureg.min,
                'distance': ((10000/1500) * ureg.min * 350 * ureg.kts).to(ureg.km),
            },
            "15000_24000": {
                'alt_bottom': 15000 * ureg.ft,
                'alt_top': 20000 * ureg.ft,
                'rate': 1000 * (ureg.ft / ureg.min),
                'v_ground': 450 * ureg.kts,
                'time': ((20000-15000)/1000) * ureg.min,
                'distance': (5 * ureg.min * 450 * ureg.kts).to(ureg.km),
            },
        }
    }
    output_data_correct = {
        "initial": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 5000 * ureg.ft,
            'rate': 2000 * (ureg.ft / ureg.min),
            'v_ground': 250 * ureg.kts,
            'time': (5000/2000) * ureg.min,
            'distance': ((5000/2000) * ureg.min * 250 * ureg.kts).to(ureg.km),
            },
        "5000_15000": {
            'alt_bottom': 5000 * ureg.ft,
            'alt_top': 15000 * ureg.ft,
            'rate': 1500 * (ureg.ft / ureg.min),
            'v_ground': 350 * ureg.kts,
            'time': (10000/1500) * ureg.min,
            'distance': ((((15000-5000))/1500) * ureg.min * 350 * ureg.kts).to(ureg.km),
        },
        "15000_24000": {
            'alt_bottom': 15000 * ureg.ft,
            'alt_top': 20000 * ureg.ft,
            'rate': 1000 * (ureg.ft / ureg.min),
            'v_ground': 450 * ureg.kts,
            'time': ((20000-15000)/1000) * ureg.min,
            'distance': (5 * ureg.min * 450 * ureg.kts).to(ureg.km),
        },
    }
    output_data_correct['15000_24000']['distance'] = input_data['distance_traveled'] - (output_data_correct['initial']['distance'] + output_data_correct['5000_15000']['distance'])
    output_data_correct['15000_24000']['time'] = (output_data_correct['15000_24000']['distance'] / (output_data_correct['15000_24000']['v_ground'])).to('min')
    output_data_correct['15000_24000']['alt_top'] = output_data_correct['15000_24000']['alt_bottom'] + (output_data_correct['15000_24000']['rate'] * (output_data_correct['15000_24000']['time'])).to('ft')
    return input_data, output_data_correct


@pytest.fixture
def distance_and_time_based_on_distance_2() -> tuple[dict, dict]:
    input_data = {
        'distance_traveled': 200 * ureg.km,
        'segments': {
            "approach": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 10000 * ureg.ft,
                'rate': 500 * (ureg.ft / ureg.min),
                'v_ground': 200 * ureg.kts,
                'time': (10000/500) * ureg.min,
                'distance': ((10000/500) * ureg.min * 200 * ureg.kts).to(ureg.km),
            },
            "24000_to_10000": {
                'alt_bottom': 10000 * ureg.ft,
                'alt_top': 24000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 400 * ureg.kts,
                'time': (14000/1500) * ureg.min,
                'distance': ((14000/1500) * ureg.min * 400 * ureg.kts).to(ureg.km),
            },
            "cruise_to_24000": {
                'alt_bottom': 24000 * ureg.ft,
                'alt_top': 32000 * ureg.ft,
                'rate': 1000 * (ureg.ft / ureg.min),
                'v_ground': 500 * ureg.kts,
                'time': ((32000-24000)/1000) * ureg.min,
                'distance': (8 * ureg.min * 500 * ureg.kts).to(ureg.km),
            },
        }
    }
    output_data_correct = {
        "approach": {
            'alt_bottom': 0 * ureg.ft,
            'alt_top': 10000 * ureg.ft,
            'rate': 500 * (ureg.ft / ureg.min),
            'v_ground': 200 * ureg.kts,
            'time': (10000/500) * ureg.min,
            'distance': ((10000/500) * ureg.min * 200 * ureg.kts).to(ureg.km),
        },
        "24000_to_10000": {
            'alt_bottom': 10000 * ureg.ft,
            'alt_top': 24000 * ureg.ft,
            'rate': 1500 * (ureg.ft / ureg.min),
            'v_ground': 400 * ureg.kts,
            'time': (14000/1500) * ureg.min,
            'distance': ((14000/1500) * ureg.min * 400 * ureg.kts).to(ureg.km),
        },
    }
    output_data_correct['24000_to_10000']['distance'] = input_data['distance_traveled'] - output_data_correct['approach']['distance']
    output_data_correct['24000_to_10000']['time'] = (output_data_correct['24000_to_10000']['distance'] / (output_data_correct['24000_to_10000']['v_ground'])).to('min')
    output_data_correct['24000_to_10000']['alt_top'] = output_data_correct['24000_to_10000']['alt_bottom'] + (output_data_correct['24000_to_10000']['rate'] * (output_data_correct['24000_to_10000']['time'])).to('ft')
    return input_data, output_data_correct


@pytest.fixture
def segments_for_function() -> tuple[float, dict, float]:
    input_data = {
        'x': 160 * ureg.km,
        'segments': {
            "approach": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 10000 * ureg.ft,
                'rate': 500 * (ureg.ft / ureg.min),
                'v_ground': 200 * ureg.kts,
                'time': (10000/500) * ureg.min,
                'distance': ((10000/500) * ureg.min * 200 * ureg.kts).to(ureg.km),
            },
            "24000_to_10000": {
                'alt_bottom': 10000 * ureg.ft,
                'alt_top': 24000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 400 * ureg.kts,
                'time': (14000/1500) * ureg.min,
                'distance': ((14000/1500) * ureg.min * 400 * ureg.kts).to(ureg.km),
            }
        }
    }
    k = input_data['segments']['24000_to_10000']['rate']/input_data['segments']['24000_to_10000']['v_ground']
    d = input_data['segments']['24000_to_10000']['alt_bottom']
    offset = input_data['segments']['approach']['distance']
    output_data = (k * (input_data['x'] - offset) + d).to('ft')
    return input_data, output_data


@pytest.fixture
def top_of_climb() -> tuple[float, dict, dict]:
    input_data = {
        'flight_distance': 15 * ureg.km,
        'climb_segments': {
            "initial": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 5000 * ureg.ft,
                'rate': 2000 * (ureg.ft / ureg.min),
                'v_ground': 250 * ureg.kts,
                'time': (5000/2000) * ureg.min,
                'distance': ((5000/2000) * ureg.min * 250 * ureg.kts).to(ureg.km),
            },
        },
        'descent_segments': {
            "approach": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 10000 * ureg.ft,
                'rate': 500 * (ureg.ft / ureg.min),
                'v_ground': 200 * ureg.kts,
                'time': (10000/500) * ureg.min,
                'distance': ((10000/500) * ureg.min * 200 * ureg.kts).to(ureg.km),
            }
        }
    }
    k_1 = input_data['climb_segments']['initial']['rate']/input_data['climb_segments']['initial']['v_ground']
    k_2 = -1 * input_data['descent_segments']['approach']['rate']/input_data['descent_segments']['approach']['v_ground']
    d_1 = 0 * ureg.ft
    d_2 = input_data['flight_distance'] * (-1) * k_2
    output_data = ((d_1-d_2)/(k_2-k_1)).to('km')

    return input_data, output_data


@pytest.fixture
def segments_for_dataframe() -> tuple[dict, dict]:
    input_data = {
        'distance_route': 400 * ureg.km,
        'climb_segments': {
            "initial": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 5000 * ureg.ft,
                'rate': 2000 * (ureg.ft / ureg.min),
                'v_ground': 250 * ureg.kts,
                'time': (5000/2000) * ureg.min,
                'distance': ((5000/2000) * ureg.min * 250 * ureg.kts).to(ureg.km),
            },
            "5000_15000": {
                'alt_bottom': 5000 * ureg.ft,
                'alt_top': 10000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 350 * ureg.kts,
                'time': ((10000-5000)/1500) * ureg.min,
                'distance': ((((10000-5000))/1500) * ureg.min * 350 * ureg.kts).to(ureg.km),
            },
        },
        'descent_segments': {
            "approach": {
                'alt_bottom': 0 * ureg.ft,
                'alt_top': 10000 * ureg.ft,
                'rate': 1000 * (ureg.ft / ureg.min),
                'v_ground': 200 * ureg.kts,
                'time': (10000/1000) * ureg.min,
                'distance': ((10000/1000) * ureg.min * 200 * ureg.kts).to(ureg.km),
            },
            "24000_to_10000": {
                'alt_bottom': 10000 * ureg.ft,
                'alt_top': 24000 * ureg.ft,
                'rate': 1500 * (ureg.ft / ureg.min),
                'v_ground': 400 * ureg.kts,
                'time': (14000/1500) * ureg.min,
                'distance': ((14000/1500) * ureg.min * 400 * ureg.kts).to(ureg.km),
            }
        },
    }
    output_data = {
        ((5000/2000) * ureg.min * 250 * ureg.kts).to(ureg.km): 5000 * ureg.ft,
        200 * ureg.km: 10000 * ureg.ft,
        (400 * ureg.km) - ((10000/1000) * ureg.min * 200 * ureg.kts).to(ureg.km): 10000 * ureg.ft,
    }
    return input_data, output_data