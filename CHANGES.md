# `jetfuelburn` Changelog

The format of this log is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## `4.0.0` (16. October 2026)

### Breaking Changes

Old names remain available as deprecated aliases: they point to the new class and figure functions.

| Module | Before (3.4.0) | After (4.0.0) |
|---|---|---|
| `reducedorder` | `<model>.calculate_fuel_consumption()` | `<model>.calculate()` |
| `reducedorder`, `statistics`, `utility.aerodynamics` | `<class>.available_aircraft()` | `<class>.list_aircraft()` |
| `statistics` | `usdot.available_years()` | `usdot.list_years()` |
| `statistics` | `usdot.calculate_fuel_consumption_per_seat()` | `usdot.calculate_per_seat()` |
| `statistics` | `usdot.calculate_fuel_consumption_per_weight()` | `usdot.calculate_per_weight()` |
| `rangeequation` | `calculate_fuel_consumption_breguet()` | `range_equation.calculate()` |
| `rangeequation` | `calculate_fuel_consumption_breguet_improved()` | `range_equation.calculate_improved()` |
| `rangeequation` | `calculate_fuel_consumption_stepclimb_integration()` | `range_equation.calculate_stepclimb_integration()` |
| `rangeequation` | `calculate_fuel_consumption_stepclimb_arctan()` | `range_equation.calculate_stepclimb_arctan()` |
| `diagrams` | `calculate_fuel_consumption_payload_range()` | `payload_range.calculate()` |
| `utility.aerodynamics` | `openap_drag_polars`, `jsbsim_drag_polars` | `poll_schumann_drag_polars` |
| `figures.aerodynamics` | `figure_openap_dragpolar()`, `figure_jsbsim_dragpolar_mach_effects()` | `figure_poll_schumann_dragpolar()` |

- Airport lookups in `utility.geography` follow the new airport list. Codes of closed or re-coded airports and some former airport names now raise a `ValueError` in `calculate_distance_between_airports()`.
- Aircraft are identified by ICAO designators throughout: e.g. 'Boeing 737 MAX 7' becomes `B37M`, 'E175' becomes `E75L` and 'Airbus A321neo' becomes `A21N`, etc.
- `statistics.aeromaps` and its data in `data/AeroMaps` are removed.
- The unimplemented `closedform` module and the `figures.benchmarking` and `figures.realdata` stubs are removed.
- `utility.tests`, the pytest-based comparison helpers, moved out of the package into the test suite (`tests/helpers.py`).

### Improvements

- Added `reducedorder.gossling_etal`, a private-jet fuel burn model by Gössling, Humpe & Leitão (2024) for 69 business and private jet types.
- Added `reducedorder.turgut_etal`, a cruise fuel-flow model by Turgut et al. (2014) for five narrow-body types.
- Added `reducedorder.models_for_aircraft()`, which lists the reduced-order models that support a given aircraft type.

### Changed

- The airport list used by `utility.geography` now uses [OurAirports](https://ourairports.com/data/) (public domain). The list now contains 11,763 airports (9,051 IATA and 10,530 ICAO codes) and corrects coordinates that the old list had wrong by up to 14,450 km (e.g. `GBI`, `SHO`, `KUR`).
- `reducedorder.seymour_etal` now uses the coefficients published in Table M.7 of the Supplementary Information of Seymour et al. (2020). They replace the values of the FEAT GitHub `.csv` file, an earlier fit committed in June 2020. The 133 aircraft types stay the same.
- `utility.aerodynamics.poll_schumann_drag_polars` implements the clean-configuration drag polar of Poll & Schumann (2025) for the 67 aircraft types of their Table 2, with a Reynolds-number-dependent zero-lift drag and wave drag. It replaces the OpenAP drag polars and the JSBSim/FlightGear drag tables, which are no longer bundled.
- The package now ships `NOTICE.md`, which lists the source, copyright holder and licence of all bundled third-party data. Each class that uses such data has a short Licensing Note that points to it.

### Fixes

- `reducedorder.seymour_etal.calculate()` squared the first coefficient (`a1**2 * R`), which dropped the quadratic term in all earlier releases. It now evaluates $F = a_1 R^2 + a_2 R + c$. Together with the new coefficients, results rise by a median of 3.5 % at 1,000 km, 9 % at 3,000 km and 19 % at 6,000 km (over the types whose maximum range in Table L.6 of the Supplementary Information reaches the distance). Results for the 26 types with a negative quadratic coefficient fall below those of earlier releases at long range, and `calculate()` raises a `ValueError` where such a fit no longer returns a positive fuel burn.
- `reducedorder.myclimate` had the coefficients of the A320 and the B737 swapped. They now match the parameter tables of the myclimate Calculation Principles page.

## `3.4.0` (14. July 2026)

### Improvements

- Improved the descent logic of `utility.ofp.generate_4d_trajectory`: the aircraft now holds its altitude until the Top of Descent (TOD) and then descends so as to reach each waypoint's target altitude exactly on arrival, re-evaluating the descent rate as it passes through successive altitude regimes (previously it began descending immediately). Added a regression test for descent from the TOD.

### Fixed

- The bundled EUROCONTROL APD sample performance dataset is now included in installed packages. It was previously stored as `data.yaml`, which the package-data configuration (matching only `*.json`, `*.csv`, and `*.gz`) excluded from the built distribution, so `utility.ofp` lookups against the shipped dataset failed for installed users. It is now stored as `data.json` and packaged correctly.

### Changed

- Aircraft performance data for `utility.ofp` is now stored as JSON and read with the standard-library `json` module instead of YAML, removing the (previously only transitively satisfied) `PyYAML` dependency.
- Documentation is now built with [Zensical](https://zensical.org), the successor to Material for MkDocs.

## `3.3.0` (12. May 2026)

### Improvements

- Added the `usdot_plots.ipynb` notebook to `processing/usdot/`, which generates plots from US DOT T2 data.
- Added benchmarking scripts and notebooks to `dev/usdot_benchmarking/`:
    - `distance_sweep.py`: sweeps trip distances from 1,000 to 7,000 km and computes fuel burn per passenger-km for all reduced-order models (`sacchi_etal`, `yanto_etal`, `montlaur_etal`, `seymour_etal`, `aim2015`, `eea_emission_inventory_2009`, `myclimate`) for representative aircraft types (A320, B738, B772), benchmarked against US DOT statistical data.
    - `ozempic_savings.ipynb` and `model_comparison.ipynb`: notebooks for visualising and comparing model outputs by modifying payload.
- Extended the `statistics.usdot` class with data for years 2019, 2023, and 2025 (previously only 2013, 2018, and 2024 were available).
- Added the following functions to the `statistics.usdot` class:
    - `calculate_movements()`: returns the number of flights captured for a given aircraft type and year.
    - `calculate_average_time()`: returns the average trip flight time for a given aircraft type and year.
    - `calculate_average_distance()`: returns the average trip distance for a given aircraft type and year.
    - `calculate_average_cargo()`: returns the average freight and mail transported for a given aircraft type and year.
    - `calculate_average_pax()`: returns the average number of passengers per flight for a given aircraft type and year.
    - `calculate_total_fuel_consumption()`: returns the total fuel consumption across all aircraft types for a given year.

## `3.2.0` (12. May 2026)

## Improvements

- Added additional regression coefficients for military and transport aircraft to the `reducedorder.eea_emission_inventory_2009` module for improved fuel burn estimation accuracy.

## `3.1.0` (16. March 2026)

## Fixes

- Updated the `utility.mapping` module to improve route rendering and label display.

## `3.0.0` (16. March 2026)

## Improvements

- Added a new `utility.mapping` module for mapping-related calculations.
- Added a new `utility.ofp` module for flight plan-related calculations.
- Updated the installation instructions to include optional dependencies.

### Breaking Changes

- Renamed the `utility.math` module to `utility.mathematics` to avoid namespace conflicts with the Python built-in `math` module.
- Renamed all variables pointing to file names to use `_path` suffix (e.g. `data.yaml` > `data_path`).

## `2.0.1` (20. February 2026)

### Fixes

- Various minor bug fixes in the test suites.

## Improvements

- Added a pre-commit hook to run the [`black` code formatter](https://github.com/psf/black) before each commit.

## `2.0.0` (11. February 2026)

### Breaking Changes

- Renamed the `breguet` module to `rangeequation`, since non-Breguet ("cruise-climb") range equation solutions have been added.
- Removed the `combined` module (which was not included in the documentation) for re-integration at a later stage.
- Renamed the `_calculate_aircraft_velocity` function in the `utility.physics` module to `_calculate_airspeed_from_mach`.

### Improvements

- Added an analytical solution ("arctan solution") to the range equation for constant altitude/airspeed flight profiles to the `rangeequation` module.
- Added a numerical solution ("integrated solution") to the range equation for variable altitude/airspeed flight profiles to the `rangeequation` module.
- Added a new `aerodynamics` utility module with functions for calculating aerodynamic properties.
    - Added a new `JSBSim` data module with aerodynamic data for the JSBSim flight dynamics model.
    - Added a new `OpenAP` data module with aerodynamic data for the OpenAP flight dynamics model.
- Added a new `engines` utility module for engine-related calculations.
    - Added a function to calculate altitude/speed-dependent engine thrust-specific fuel consumption (TSFC) based on manufacturer information.
- Added a new `math` utility module for mathematical functions.
- Added a new `code` utility module for code-related utilities.

### Fixes

- Various minor bug fixes and documentation improvements.

## `1.6.0` (01. February 2026)

## Improvements

- Updated the `utility.physics` module:
    - Removed function `_calculate_atmospheric_conditions`
    - Added function `_calculate_atmospheric_temperature`
    - Added function `_calculate_atmospheric_density`
    - Added function `_calculate_speed_of_sound`

## `1.5.2` (23. January 2026)

### Fixes

- Updated the file I/O handling in the `jetfuelburn.utility.geography` module to avoid repeated file openings when calculating Great Circle distances.

## `1.5.1` (22. January 2026)

### Improvements

- Added a function to calculate Great Circle distances between two airports to the `jetfuelburn.utility.geography` module.

## `1.4.0` (20. January 2026)

### Improvements

- Added the fuel burn model of Montlaur et al. (2025) to the `jetfuelburn.reducedorder` module.

## `1.3.0` (15. January 2026)

### Improvements

- Added the fuel burn model of @romainsacchi (2023) to the `jetfuelburn.reducedorder` module.

## `1.2.0` (14. January 2026)

### Improvements

- Added the fuel burn model of the AeroMaps software framework by Planès et al. (2023) to the `jetfuelburn.statistics` module.

## `1.1.1` (20. December 2025)

Release for Zenodo archiving and JOSS publication.

## `1.1.0` (07. October 2025)

### Improvements

- Renamed module `aux` to `utility` for consistency with other packages.

## `1.0.2` (08. August 2025)

### Improvements

- Moved to `src/jetfuelburn` directory structure.

## `1.0.1` (08. August 2025)

### Fixes

- Fixed `pint` unit registry error in `statistics` module ([#20](https://github.com/sustainableaviation/jetfuelburn/issues/20)).

## `1.0.0` (27. April 2025)

!!! note
    Initial release of `jetfuelburn` package to accompany a submission to [JOSS](https://joss.theoj.org).

### Improvements

- Updated documentation.

### Fixes

- Fixed unit conversion errors in `jetfuelburn.breguet.calculate_fuel_consumption_range_equation()` function.
- Fixed the `Examples` section of the `jetfuelburn.reducedorder.eea_emission_inventory_2009` module.

## `0.0.9` (27. April 2025) ++YANKED++

### Fixes

- Fixed `Example` sections of function/class docstrings (were named `Examples` previously).

### Improvements

- Added US Department of Transportation (USDOT) Statistical Data (Form 41 Schedule T-100 Table T2) ([#14](https://github.com/sustainableaviation/jetfuelburn/issues/14)).
- Moved `jetfuelburn.averages.myclimate` to `jetfuelburn.reducedorder.myclimate`.

## `0.0.8` (16. April 2025)

### Improvements

- Added MyClimate Average/Statistical Model ([#10](https://github.com/sustainableaviation/jetfuelburn/issues/10)).

### Fixes

- Fixed parameter description of `jetfuelburn.diagrams.calculate_fuel_consumption_payload_range()` function.

## `0.0.7` (24. March 2025)

### Improvements

- Added EMEP/EEA Emissions Model ([#5](https://github.com/sustainableaviation/jetfuelburn/issues/5)).
- Added warning and interactive plot to Lee et al. (2010) Model.

## `0.0.5` (14. March 2025)

!!! note
    First working release for testing of Pyodide "Examples" fences.

### Improvements

- Added GitHub Actions workflow files.
- Made `AIM2015` data files accessible.

## `0.0.1` (13. March 2025)

!!! note
    [Initial release](https://upload.wikimedia.org/wikipedia/en/4/4b/F111_Avalon_Airshow_2007_1.jpg), including drafts of all functions.

