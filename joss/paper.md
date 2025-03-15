---
title: 'JetFuelBurn: A Python package for calculating fuel burn of commercial aircraft.'
tags:
  - Python
  - aviation
  - efficiency
  - fuel burn
  - emissions
  - life-cycle assessment
authors:
  - name: Michael P. Weinold
    orcid: 0000-0003-4859-2650
    equal-contrib: false
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Russell McKenna
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    orcid: 0000-0001-6758-482X
    affiliation: "1, 2"
affiliations:
 - name: Laboratory for Energy Systems Analysis, PSI Centers for Nuclear Engineering \& Sciences and Energy \& Environmental Sciences, Villigen, Switzerland
   index: 1
 - name: Chair of Energy Systems Analysis, Institute of Energy and Process Engineering, Department of Mechanical and Process Engineering, ETH Zurich, Zurich, Switzerland
   index: 2
date: 14 March 2025
bibliography: paper.bib

---

# Summary



# Statement of Need

Environmental assessment of air travel is important
In the life-cycle assessment of aviation, the use-phase of the aircraft has by far the largest impact on the environment.
The fuel burn of an aircraft is a key parameter in the environmental assessment of air travel. The other key parameter is the environmental burdens associated with fuel burn
Unforuntaly, environmental researchers are often using overly simplistic models to calculate fuel burn.
Recently, Su-Un... [@su2023methodological] in Science of the Total Environment...
Sacchi et al. [@sacchi2023make] based on work by Cox, which was based on ....


Tools include:

| Tool                                    | Provider  | Availability    | Data Sources                                                   |
|-----------------------------------------|-----------|-----------------|----------------------------------------------------------------|
| ICAO Carbon Emissions Calculator (ICEC) | ICAO      | Public (Online) | "ICAO Fuel Formulas"                                           |
| IATA CO2 Connect                        | IATA      | Proprietary     | airline statistics (real flights)                              |
| myClimate CO2 Flight Calculator         | myClimate | Public (Online) | EMEP/EEA air pollutant emission inventory guidebook            |
| Google Flights                          | Google    | Public (Online) | "travel-impact-model" (data partially from EMEP/EEA guidebook) |


While researchers from aerospace engineering have proposed different approaches, few have been implemented in a user-friendly package that can be used by non-experts.
The `jetfuelburn` package is the first Python package that provides a comprehensive set of fuel burn models for commercial aircraft. It is designed to be used in the context of environmental impact assessment of air travel, aircraft performance analysis and optimisation. It uses the `pint` package to allow for calculations in physical units, allowing for quick conversion between imperial and metric units. In addition, all variables passed to functions are checked for correct physical dimensions.


Is going to be a great addition to existing fuel burn calculators, etc.

# Fuel Calculation Model Categories

The `jetfuelburn` package implements different types of fuel burn models:

1. Breguet Range Equation
2. Payload/Range Diagrams
3. Reduced Order Models
4. Combined Models

Lee et al. (2010)[@lee2010closed]
and
Yanto et al. (2017)[@yanto2017efficient]


# Auxiliary Functions

The `jetfuelburn` package also includes helper functions for basic atmospheric physics and the allocation of fuel burn to different cabin classes (economy, business, etc.).

# Figures


Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](docs/_static/payload_range_generic.svg){ width=20% }

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation. The authors would like to thank Dr. Peter Wild of SWISS Intl. Airlines for providing valuable feedback during the development of this package.

# References