# Reduced Order Models (External)

## OpenAP Model

[OpenAP (Open Aircraft Performance Model and Toolkit)](https://openap.dev) is an open-source Python library developed by researchers at TU Delft for aircraft performance and emission calculations. 
The library also includes modules for drag, thrust, kinematic modeling, and trajectory generation.

### Fuel and Emission Module

The OpenAP fuel module uses polynomial models derived from the 
[ICAO Engine Emissions Databank](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) and the [Acropole model](https://github.com/junzis/acropole).

- The `FuelFlow()` class computes instantaneous fuel consumption for different flight phases (taxi, takeoff, climb, cruise, descent) based on aircraft mass, true airspeed (TAS), and altitude.  
- The `Emission()` class calculates pollutant emissions (NOₓ, CO, HC) using corresponding ICAO engine emission data.

### Full Flight Trajectory Input Requirement
The OpenAP model requires a full flight trajectory as a time-series input to compute fuel consumption and emissions across all flight phases. This trajectory is typically provided as a tabular structure (e.g., a Pandas DataFrame) describing the aircraft’s state at regular time intervals.

| Required Kinematic Input Columns | Description                                                     |
|----------------------------------|-----------------------------------------------------------------|
| `mass` or `m0`                   | Aircraft mass (Take-off mass is needed for initialization)      |
| `tas`                            | True Airspeed throughout the flight                             |
| `h` or `altitude`                | Altitude throughout the flight                                  |
| `vs` or `vertical_rate`          | Vertical speed throughout the flight                            |

### Trajectory Acquisition

Flight trajectories can be obtained in two ways:

1. Generation: Using the `FlightGenerator` class in the `openap.gen` module to synthesize representative trajectories.
2. Actual Flight Data: Importing real flight trajectories from ADS-B data providers such as OpenSky Network, Flightradar24, or airplanes.live.

!!! reference "References"
    Sun, J., Hoekstra, J. M., & Ellerbroek, J. (2020). OpenAP: An open-source aircraft performance model for air transportation studies and simulations. *Aerospace*, 7(8), 104. doi:[10.3390/aerospace7080104](https://doi.org/10.3390/aerospace7080104)
    
!!! reference "See Also"
    - [OpenAP Handbook](https://openap.dev)
    - [Fuel and Emission Module Documentation](https://openap.dev/fuel_emission.html)
    - [Trajectory Generation Documentation](https://openap.dev/trajectory_gen.html)
    - [GitHub Repository](https://github.com/junzis/openap)

!!! warning
    The interactive code editor below is based on the Pyodide web assembly Python distribution. It runs Python code in a browser sandbox. 
    This sandbox has certain limitations, [such as HTTP client functionality](https://pyodide.org/en/stable/usage/api/python-api/http.html). 
    In order to load a csv file from a URL, instead of:

    ```python
    import pandas as pd
    df = pd.read_csv('https://example.com/data.csv')
    ```

    the following approach must be used:

    ```python
    import pandas as pd
    from pyodide.http import open_url
    df = pd.read_csv(open_url('https://example.com/data.csv'))
    ```

!!! example "Usage Example"
    ```pyodide install='openap' 
    from openap import FuelFlow
    import pandas as pd
    from pyodide.http import open_url

    fuelflow = FuelFlow('A319')
    mass_takeoff_assumed = 66300  # kg, this model only supports kilograms as input unit

    df = pd.read_csv(
        open_url('https://raw.githubusercontent.com/junzis/openap/refs/heads/master/examples/data/flight_a319_opensky.csv'),
        parse_dates=['timestamp'],
        dtype={'icao24': str},
    )

    # Calculate time deltas between consecutive points
    df = df.assign(d_ts=lambda d: d.timestamp.diff().dt.total_seconds().bfill())
    
    # Calculate fuel burn at each trajectory point
    mass_current = mass_takeoff_assumed
    fuelflow_every_step = []
    fuel_every_step = []

    for i, row in df.iterrows():
        # Calculate instantaneous fuel flow
        ff = fuelflow.enroute(
            mass=mass_current,
            tas=row.groundspeed,
            alt=row.altitude,
            vs=row.vertical_rate,
        )
        fuel = ff * row.d_ts
        fuelflow_every_step.append(ff)
        fuel_every_step.append(fuel)
        mass_current -= fuel

    # Add results to dataframe
    df = df.assign(fuel_flow=fuelflow_every_step, fuel=fuel_every_step)

    # Calculate total fuel consumed
    total_fuel = df.fuel.sum().astype(int)
    print(f'Total fuel: {total_fuel} kg')
    ```