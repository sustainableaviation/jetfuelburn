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

`jetfuelburn` is a Python package that implements different methods for calculating the fuel burn of commercial passenger aircraft. It is designed to be used in the context of environmental impact assessment of air travel, aircraft performance analysis and optimisation. It supports calculations in physical units, allowing for quick conversion between imperial and metric units and dimensionality checks of function inputs. It is lightweight (<40kB packaged) and has only a single dependency (`pint`), therefore allowing for easy integration into WebAssembly kernels for interactive use in the browser. The package is open-source and distributed under a permissive MIT license.

# Statement of Need

The environmental assessment of air travel has received increasing attention in the context of efforts to decarbonize transportation. In this context, life-cycle assessment has emerged as the primary method used to evaluate the magnitude of environmental burdens [@keiser2023life]. In air travel specifically, it has been shown that _"The most important life sequence is the use sequence, which makes up over 99\% of emission for every aircraft."_ [@jakovljevic2018carbon, P.865].

Central to any evaluation of the environmental impact of air travel are therfore two key parameters: The fuel burn of the aircraft itself and the environmental burdens associated with the fuel used. Reliable methods for estimating both quantities are essential for providing reliable estimates of the carbon footprint of air travel.

Unfortunately, environmental researchers often rely on overly simplistic models to estimate fuel burn, leading to flawed conclusions. For instance, a recent study by Su-Un et al. (2023) published in Science of the Total Environment [@su2023methodological] assumed that aircraft could be fully fueled, fully loaded, and still achieve maximum range—an unrealistic scenario that results in a significant underestimation of fuel burn and, consequently, its environmental impact. If tools are available, they are often proprietary or cannot easily be adapted for future aircraft. A selection of current air travel CO~2~ calculators and their availability is shown in the table below:

| Tool               | Provider  | Availability    | Data Sources               |
|--------------------|-----------|-----------------|----------------------------|
| ICEC               | ICAO      | Open            | "ICAO Fuel Formulas"       |
| CO~2~ Connect      | IATA      | Proprietary     | airline statistics         |
| CO~2~ Flight Calc. | myClimate | Open            | EMEP/EEA emissions guideb. |
| Google Flights     | Google    | Open            | `travel-impact-model`      |

To remedy this problem, researchers from aerospace engineering have proposed different approaches, few have been implemented in a user-friendly package that can be used by non-experts.
The `jetfuelburn` package is the first Python package that provides a comprehensive set of fuel burn models for commercial aircraft. It is designed to be used in the context of environmental impact assessment of air travel, aircraft performance analysis and optimisation. It uses the `pint` package to allow for calculations in physical units, allowing for quick conversion between imperial and metric units. In addition, all variables passed to functions are checked for correct physical dimensions.

Is going to be a great addition to existing fuel burn calculators, etc.

# Fuel Calculation Model Categories

The `jetfuelburn` package implements different types of fuel burn models. The simplest models are based on basic aerodynamic equations like the Breguet range equation, while more complex models take into account the specifics of different aircraft types. The package includes the following models:

| Model Category    | Description | Methods |
|--------------------|-----------|------------|
| Breguet Range Equation | Simple model based on the Breguet range equation | [@young2017performance] |
| Payload/Range Diagrams | Model based on payload/range diagrams | [@burzlaff2017aircraft] |
| Reduced Order Models | Model based on reduced order models | [@lee2010closed] [@yanto2017efficient][@dray2019aim2015][@seymour2020fuel] |
| Combined Models | Models that combine different methods | new |




# Auxiliary Functions

The `jetfuelburn` package includes helper functions for basic problems in atmospheric physics, such as computation of airspeed from mach number based on ambient pressure. In addition, the package includes a module for the allocation of fuel burn to different cabin classes (economy, business, etc.) according to the current approach of both [IATA]((https://web.archive.org/web/20230526103741/https://www.iata.org/contentassets/139d686fa8f34c4ba7a41f7ba3e026e7/iata-rp-1726_passenger-co2.pdf)) and [ICAO]((https://web.archive.org/web/20240826103513/https://applications.icao.int/icec/Methodology%20ICAO%20Carbon%20Emissions%20Calculator_v13_Final.pdf)).

# Interactive Documentation

The package documentation allows users to compute fuel burn directly in the browser, without the need to install the package locally. This is achieved through the use of a [Pyodide](https://pyodide.org/en/stable/) Web Assembly Python kernel. The interactive documentation is available at [jetfuelburn.readthedocs.io](https://jetfuelburn.readthedocs.io).

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation. The authors would like to thank Dr. Peter Wild of SWISS Intl. Airlines for providing valuable feedback during the development of this package.

# References