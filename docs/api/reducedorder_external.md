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



## Travel Impact Model (Google)

The Google [Travel Impact Model (TIM)](https://travelimpactmodel.org) estimates flight fuel consumption and associated emissions using the Tier 3A methodology (flight-specific, Origin-Destination approach) defined in the EMEP/EEA Annex 1.A.3.a Aviation 2023. For each scheduled flight, fuel consumption is calculated by combining data from standard databases for two phases:

- **LTO phase (Taxi, Takeoff, Landing):** Fixed fuel burn calculated using [ICAO Aircraft Engine Emissions Databank (AEED)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) standards (LTO cycle fuel flow/emission indices).
- **CCD phase (Climb, Cruise, Descent):** Variable fuel burn derived from EUROCONTROL Advanced Emission Model (AEM)/Base of Aircraft Data (BADA) performance modeling, adjusted for real-world routing and calculated via linear interpolation/extrapolation for stage length.

Total fuel is converted to CO₂-equivalent using [ISO 14083](https://www.iso.org/standard/78864.html)-compliant Well-to-Wake (WTW) life-cycle factors (3.8359 kg CO₂e/kg fuel). The final passenger estimate is derived via a three-step apportionment process: allocating total emissions between cargo and passenger payloads using the mass-based approach, normalizing passenger count via statistical load factors, and applying cabin class weightings based on actual or median seat configuration data.

This model is integrated into the Google Flights interface and displays the CO₂-equivalent values to users searching for flight options:

![Google Flights showing Travel Impact Model emissions](../_static/screenshots/google_flights_tim.png)
*Example of CO₂ emissions displayed in Google Flights search results.*

!!! note
    The Travel Impact Model can also be accessed via a free, publicly available API provided by Google. The API allows developers to retrieve flight-level CO₂e emission estimates by specifying the following parameters: origin, destination, operating carrier, flight number, and departure date. For more information, see the [Google Travel Impact Model API documentation](https://developers.google.com/travel/impact-model).

!!! note
    The Travel Impact Model in Google Flights only shows emissions for _future_ flights (which can still be booked). It does not provide emissions data for past flights.

!!! note "Integration with EU Flight Emissions Label (FEL)"
    The **Travel Impact Model (TIM)** integrates the **EU Flight Emissions Label (FEL)** through its distribution network, ensuring interoperability between the two methodologies. For flights with FEL data issued by EASA, these verified values **replace TIM estimates** and are clearly marked as “EASA” to indicate the source. For more information, see the [Flight Emissions Label section of the Travel Impact Model documentation](https://github.com/google/travel-impact-model?tab=readme-ov-file#flight-emissions-label).

!!! reference "See Also"
    - [Google Travel Impact Model Website](https://travelimpactmodel.org)
    - [Google Travel Impact Model API Documentation](https://developers.google.com/travel/impact-model)

!!! reference "References"
    [EMEP/EEA Air Pollutant Emission Inventory Guidebook 2023 (Annex 1.A.3.a Aviation)](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023)
