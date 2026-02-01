# `jetfuelburn` Changelog

The format of this log is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

