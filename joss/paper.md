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

`jetfuelburn` is a Python package that implements different methods for calculating the fuel burn of commercial passenger aircraft. It is designed to be used in the context of environmental impact assessment of air travel, aircraft performance analysis and optimisation. It supports calculations in physical units, allowing for quick conversion between imperial and metric units and dimensionality checks of function inputs. It is lightweight (<40kB packaged) and has only a single dependency (`pint`), therefore allowing for easy integration into WebAssembly kernels for interactive use in the browser. The package is open-source and distributed under a permissive MIT license. Interactive documentation is available, which allows users to compute fuel burn directly in the browser without the need to install the package locally.

# Statement of Need

The environmental assessment of air travel has received increasing attention in the context of efforts to decarbonize transportation. In this context, life-cycle assessment has emerged as the primary method used to evaluate the magnitude of environmental burdens [@keiser2023life]. In air travel specifically, it has been shown that _"The most important life sequence is the use sequence, which makes up over 99\% of emission for every aircraft."_ [@jakovljevic2018carbon, P.865]. Robust methods for computing two key parameters are therefore central to any reliable evaluation of the environmental impact of air travel: The fuel burn of the aircraft itself and the environmental burdens associated with fuel production.

While researchers in aerospace engineering have therefore proposed various methods for estimating the fuel burn of commercial aircraft, few of these have been incorporated into software packages, particularly in a lightweight, user-friendly Python format. To address this gap, the `jetfuelburn` package has been developed as the first comprehensive Python tool offering a robust set of fuel burn models for commercial aircraft. Designed for applications such as environmental impact assessments of air travel, aircraft performance analysis, and optimization, this package promises to be a valuable enhancement to existing fuel burn calculators and related tools.

\clearpage

# Fuel Calculation Model Categories

The `jetfuelburn` package includes different methods for calculating fuel burn of commercial aircraft. These methods can be broadly categorized into four groups:

## Payload/Range Diagrams

As an initial estimate, the fuel burn of aircraft can be "read off" payload/range diagrams directly [@burzlaff2017aircraft]. The `jetfuelburn` package includes a method for this purpose.

## Range Equation

The Breguet range equation is a simple model that relates the range of an aircraft to its fuel burn and efficiency. The `jetfuelburn` package includes a method for calculating fuel burn based on the Breguet range equation [@young2017performance, Sec. 13.7.3].

## Reduced Order Models

If access to propriatary aircraft performance simulation software is available, fuel burn for specific aircraft missions can be simulated with high resolution. However, these simulations can be computationally expensive. Reduced order models instead use regression to extract a simplified model from a large set of high resolution simulation results. While the simulations may include many aircraft and mission parameters, reduced order models only require a few key parameter, such as payload and range. 

The present verion of the `jetfuelburn` package implements four different reduced order models, proposed by [@lee2010closed;@yanto2017efficient;@dray2019aim2015;@seymour2020fuel].

# Auxiliary Functions

The `jetfuelburn` package includes helper functions for basic problems in atmospheric physics, such as computation of airspeed from mach number based on ambient pressure. In addition, the package includes a module for the allocation of fuel burn to different cabin classes (economy, business, etc.) according to the current approach of both [IATA]((https://web.archive.org/web/20230526103741/https://www.iata.org/contentassets/139d686fa8f34c4ba7a41f7ba3e026e7/iata-rp-1726_passenger-co2.pdf)) and [ICAO]((https://web.archive.org/web/20240826103513/https://applications.icao.int/icec/Methodology%20ICAO%20Carbon%20Emissions%20Calculator_v13_Final.pdf)).

# Future Development

Recent work has shown that highly accurate (1-2% deviation from real flight data) closed-form solutions to fuel burn equations can be derived from first principles [@poll2025estimation]. Required aircraft-specific input parameters can be extracted from publicly available sources. These novel methods can be implemented in future versions of the `jetfuelburn` package. 

# Interactive Documentation

The package documentation allows users to compute fuel burn directly in the browser, without the need to install the package locally. This is achieved through the use of a [Pyodide](https://pyodide.org/en/stable/) Web Assembly Python kernel. The interactive documentation is available at [jetfuelburn.readthedocs.io](https://jetfuelburn.readthedocs.io).

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation. The authors would like to thank Dr. Peter Wild of SWISS Intl. Airlines for providing valuable feedback during the development of this package.

# References