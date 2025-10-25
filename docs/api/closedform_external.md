# Closed Form Models (External)

## Poll–Schumann Model (via `pycontrails`)

The Poll–Schumann model provides a closed-form, physics-based method to estimate aircraft fuel flow and performance along flight trajectories. It is implemented in [`pycontrails`](https://py.contrails.org), an open-source library for modeling contrails and aviation climate impacts.

The model analytically links fuel burn, specific range, and aerodynamic efficiency using parameters such as:

- Aircraft mass and lift-to-drag ratio
- Thrust setting and Mach number
- Atmospheric temperature and pressure

The implementation in `pycontrails` (`PollSchumann` class) computes instantaneous fuel flow and total burn over a trajectory segment from inputs like altitude, TAS, Mach, and mass.

!!! note
    The Poll-Schumann Model requires a full flight trajectory as input for fuel calculations.

!!! reference "References"
    - Poll, D. I. A., & Schumann, U. (2025). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft; part 3 full flight profile when the trajectory is specified. *The Aeronautical Journal*, 1-37. doi:[10.1017/aer.2024.141](https://doi.org/10.1017/aer.2024.141)
    - Poll, D. I. A., & Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft during cruise. part 2, determining the aircraft's characteristic parameters. *The Aeronautical Journal*, 125(1284), 296-340. doi:[10.1017/aer.2020.124](https://doi.org/10.1017/aer.2020.124)
    - Poll, D. I. A., & Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft in the cruise. Part 1 fundamental quantities and governing relations for a general atmosphere. *The Aeronautical Journal*, 125(1284), 257-295. doi:[10.1017/aer.2020.62](https://doi.org/10.1017/aer.2020.62)
    - [`pycontrails` AircraftPerformance module](https://py.contrails.org/notebooks/AircraftPerformance.html)  
    - Project site: [contrails.org](https://contrails.org)


