import pandas as pd
import numpy as np
import polars as pl
from pathlib import Path
from jetfuelburn import ureg
from jetfuelburn.utility.ofp import generate_4d_trajectory

# Create a mock OFP dataframe (Polars as expected by the function's type hint, 
# although the function seems to use pandas methods on it... wait, let's check the function code again)
# The function call says 'df_ofp: pl.DataFrame' but the implementation uses '.copy()', '.cumsum()', '.resample()'
# which are Pandas methods. So it actually takes a Pandas DataFrame but hints Polars?
# Let's check the imports in ofp.py.

df_ofp = pd.DataFrame({
    'waypoint': ['WP1', 'WP2', 'WP3'],
    'alt': [0.0, 'CLB', 10000.0],
    'timecum': [0.0, 10.0, 20.0],
    'lat': [37.0, 38.0, 39.0],
    'lon': [-122.0, -121.0, -120.0]
})

perf_data_path = Path("/tmp/mock_perf.yaml")
import yaml
mock_data = {
    "B123": {
        "climb": [
            {"min_alt": "0 ft", "max_alt": "20000 ft", "rate": "2000 ft/min", "regime": "climb"}
        ],
        "descent": [
            {"min_alt": "20000 ft", "max_alt": "0 ft", "rate": "-1500 ft/min", "regime": "descent"}
        ]
    }
}
with open(perf_data_path, 'w') as f:
    yaml.dump(mock_data, f)

try:
    # Note: the function implementation in ofp.py uses pandas methods on df_ofp
    df_4d = generate_4d_trajectory(
        df_ofp=df_ofp,
        aircraft_type="B123",
        perf_data_path=perf_data_path,
        time_resolution=1.0 * ureg.minute
    )
    print("Success status: Pass")
    print(df_4d[['timestamp', 'alt']].head(15))
except Exception as e:
    print(f"Success status: Fail")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    import traceback
    traceback.print_exc()
