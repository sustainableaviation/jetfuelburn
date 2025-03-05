import pytest

@pytest.fixture
def allocation_two_classes():
    input_data = {
        'fuel_per_flight': 1000,
        'size_factor_eco': 1,
        'size_factor_premiumeco': 0,
        'size_factor_business': 1.5,
        'size_factor_first': 0,
        'seats_eco': 200,
        'seats_premiumeco': 0,
        'seats_business': 14,
        'seats_first': 0,
        'load_factor_eco': 0.8,
        'load_factor_premiumeco': 0,
        'load_factor_business': 0.3,
        'load_factor_first': 0,
    }
    return input_data


@pytest.fixture
def allocation_all_classes():
    input_data = {
        'fuel_per_flight': 2000,
        'size_factor_eco': 1,
        'size_factor_premiumeco': 1.3,
        'size_factor_business': 2,
        'size_factor_first': 3,
        'seats_eco': 150,
        'seats_premiumeco': 30,
        'seats_business': 14,
        'seats_first': 6,
        'load_factor_eco': 0.8,
        'load_factor_premiumeco': 0.75,
        'load_factor_business': 0.3,
        'load_factor_first': 0.2,
    }
    return input_data
