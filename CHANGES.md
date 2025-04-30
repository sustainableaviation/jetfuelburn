# `jetfuelburn` Changelog

The format of this log is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## `1.0.0` (27. April 2025)

Initial release of `jetfuelburn` package to accompany a submission to [JOSS](https://joss.theoj.org).

- Fixed unit conversion errors in `jetfuelburn.breguet.calculate_fuel_consumption_range_equation()` function.
- Fixed the `Examples` section of the `jetfuelburn.reducedorder.eea_emission_inventory_2009` module.
- Updated documentation.

## `0.0.9` (27. April 2025) ++YANKED++

- Added US Department of Transportation (USDOT) Statistical Data (Form 41 Schedule T-100 Table T2) ([#14](https://github.com/sustainableaviation/jetfuelburn/issues/14)).
- Fixed `Example` sections of function/class docstrings (were named `Examples` previously).
- Moved `jetfuelburn.averages.myclimate` to `jetfuelburn.reducedorder.myclimate`.

## `0.0.8` (16. April 2025)

- Added MyClimate Average/Statistical Model ([#10](https://github.com/sustainableaviation/jetfuelburn/issues/10)).
- Fixed parameter description of `jetfuelburn.diagrams.calculate_fuel_consumption_payload_range()` function.

## `0.0.7` (24. March 2025)

- Added EMEP/EEA Emissions Model ([#5](https://github.com/sustainableaviation/jetfuelburn/issues/5)).
- Added warning and interactive plot to Lee et al. (2010) Model.

## `0.0.5` (14. March 2025)

!!! note
    First working release for testing of Pyodide "Examples" fences.

- Added GitHub Actions workflow files.
- Made `AIM2015` data files accessible.

## `0.0.1` (13. March 2025)

!!! note
    [Initial release](https://upload.wikimedia.org/wikipedia/en/4/4b/F111_Avalon_Airshow_2007_1.jpg), including drafts of all functions.

