import pytest

from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.statistics import usdot

def test_usdot():
    assert 2024 in usdot.available_years()
    assert 'B787-800 Dreamliner' in usdot.available_aircraft(2024)