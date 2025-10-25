# Reduced Order Models (External)

## OpenAP Model

OpenAP (Open Aircraft Performance Model and Toolkit) is an open-source Python library developed by researchers at TU Delft for aircraft performance and emission calculations. The library also includes modules for drag, thrust, kinematic modeling, and trajectory generation.

**Fuel and Emission Module:**

The OpenAP fuel module uses polynomial models derived from the ICAO Engine Emissions Databank and the Acropole model. The `FuelFlow()` class computes fuel consumption for different flight phases (taxi, takeoff, climb, cruise, descent) based on aircraft mass, true airspeed, and altitude. The `Emission()` class calculates pollutant emissions (NOx, CO, HC) using ICAO engine data.

!!! note
    The OpenAP Model requires a full flight trajectory as input for fuel calculations.

!!! reference "References"
    - Sun, J., Hoekstra, J. M., & Ellerbroek, J. (2020). OpenAP: An open-source aircraft performance model for air transportation studies and simulations. *Aerospace*, 7(8), 104. doi:[10.3390/aerospace7080104](https://doi.org/10.3390/aerospace7080104)
    - [OpenAP Handbook](https://openap.dev)
    - [Fuel and Emission Module Documentation](https://openap.dev/fuel_emission.html)
    - [GitHub Repository](https://github.com/junzis/openap)

