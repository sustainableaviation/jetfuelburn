# Closed Form Models (External)

## Poll–Schumann Model (via `pycontrails`)

The Poll–Schumann model provides a closed-form, physics-based method to estimate aircraft fuel flow and performance along flight trajectories. It is implemented in [`pycontrails`](https://py.contrails.org), an open-source library for modeling contrails and aviation climate impacts.

The model analytically links fuel burn, specific range, and aerodynamic efficiency using parameters such as:

- Aircraft mass and lift-to-drag ratio
- Thrust setting and Mach number
- Atmospheric temperature and pressure

The implementation in `pycontrails` computes instantaneous fuel flow and total burn over a trajectory segment from inputs like altitude, TAS, Mach number, and mass.

!!! note
    The Poll-Schumann Model requires a full flight trajectory as input for fuel calculations.

!!! reference "References"
    - Poll, D. I. A., & Schumann, U. (2025). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft; part 3 full flight profile when the trajectory is specified. *The Aeronautical Journal*, 1-37. doi:[10.1017/aer.2024.141](https://doi.org/10.1017/aer.2024.141)
    - Poll, D. I. A., & Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft during cruise. part 2, determining the aircraft's characteristic parameters. *The Aeronautical Journal*, 125(1284), 296-340. doi:[10.1017/aer.2020.124](https://doi.org/10.1017/aer.2020.124)
    - Poll, D. I. A., & Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft in the cruise. Part 1 fundamental quantities and governing relations for a general atmosphere. *The Aeronautical Journal*, 125(1284), 257-295. doi:[10.1017/aer.2020.62](https://doi.org/10.1017/aer.2020.62)

!!! reference "See Also"
    - [`pycontrails.models.ps_model.PSFlight`](https://py.contrails.org/api/pycontrails.models.ps_model.PSFlight.html)  
    - [contrails.org](https://contrails.org)

!!! warning
    `pycontrails`, which implements the Poll-Schumann model, is not a pure Python package and therefore not compatible with [Pyodide](https://pyodide.org/en/stable/). The below example is therefore not interactice.

!!! example "Usage Example"
    ```python
    from pycontrails import Flight
    from pycontrails.models.ps_model import PSFlight
    import pandas as pd

    flight = Flight(
        data=pd.read_csv('https://raw.githubusercontent.com/contrailcirrus/pycontrails/refs/heads/main/docs/notebooks/data/flight-ap.csv'),
        attrs={
            'flight_id': '1',
            'aircraft_type': 'A320'
        }
    )

    # Create PS Flight model and evaluate
    ps_model = PSFlight(
        fill_low_altitude_with_isa_temperature=True,
        fill_low_altitude_with_zero_wind=True,
    )
    out = ps_model.eval(flight)

    # Calculate total fuel burned from mass drop
    df = out[['time', 'aircraft_mass']].dropna().sort_values('time')
    if len(df) >= 2:
        total_fuel_kg = float(df['aircraft_mass'].iloc[0] - df['aircraft_mass'].iloc[-1])
    ```