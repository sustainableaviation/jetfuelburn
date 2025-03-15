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

| Tool               | Provider  | Availability    | Data Sources            |
|--------------------|-----------|-----------------|-------------------------|
| ICEC               | ICAO      | Open            | "ICAO Fuel Formulas"    |
| CO~2~ Connect      | IATA      | Proprietary     | airline statistics      |
| CO~2~ Flight Calc. | myClimate | Open            | EMEP/EEA emissions      |
| Google Flights     | Google    | Public          | `travel-impact-model`   |


While researchers from aerospace engineering have proposed different approaches, few have been implemented in a user-friendly package that can be used by non-experts.
The `jetfuelburn` package is the first Python package that provides a comprehensive set of fuel burn models for commercial aircraft. It is designed to be used in the context of environmental impact assessment of air travel, aircraft performance analysis and optimisation. It uses the `pint` package to allow for calculations in physical units, allowing for quick conversion between imperial and metric units. In addition, all variables passed to functions are checked for correct physical dimensions.


Is going to be a great addition to existing fuel burn calculators, etc.

# Fuel Calculation Model Categories

The `jetfuelburn` package implements different types of fuel burn models. 

1. Breguet Range Equation
2. Payload/Range Diagrams
3. Reduced Order Models
  1. [@lee2010closed]
  2. [@yanto2017efficient]
4. Combined Models


# Auxiliary Functions

The `jetfuelburn` package includes helper functions for basic problems in atmospheric physics, such as computation of airspeed from mach number based on ambient pressure. In addition, the package includes a module for the allocation of fuel burn to different cabin classes (economy, business, etc.) according to the current approach of both [IATA]((https://web.archive.org/web/20230526103741/https://www.iata.org/contentassets/139d686fa8f34c4ba7a41f7ba3e026e7/iata-rp-1726_passenger-co2.pdf)) and [ICAO]((https://web.archive.org/web/20240826103513/https://applications.icao.int/icec/Methodology%20ICAO%20Carbon%20Emissions%20Calculator_v13_Final.pdf)).

# Interactive Documentation

The package documentation allows users to compute fuel burn directly in the browser, without the need to install the package locally. This is achieved through the use of a [Pyodide](https://pyodide.org/en/stable/) Web Assembly Python kernel. The interactive documentation is available at [jetfuelburn.readthedocs.io](https://jetfuelburn.readthedocs.io).

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation. The authors would like to thank Dr. Peter Wild of SWISS Intl. Airlines for providing valuable feedback during the development of this package.

# References