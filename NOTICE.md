# Third-Party Notices

## Data licensed under MIT

### AIM2015 aircraft performance parameters (`reducedorder.aim2015`)

File: `src/jetfuelburn/data/AIM2015/AIM2015_v11_AircraftPerformanceParams.csv`

Source: `AircraftPerformanceParams.csv` from the free release of the Aviation Integrated Model (AIM2015), v11
(Air Transportation Systems Laboratory, UCL Energy Institute, February 2023), renamed, content unmodified.
AIM is released under the MIT License (AIM 2015 Documentation v11, Section 1:
"AIM is released under a MIT open source license (MIT, 2022)."),
archived at https://web.archive.org/web/20240228163837/https://www.atslab.org/wp-content/uploads/2023/02/AIM-2015-Documentation-v11.pdf

```
Copyright (c) University College London (UCL), Air Transportation Systems Laboratory (ATSLab)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## Data licensed under Creative Commons Attribution 4.0 (CC BY 4.0)

https://creativecommons.org/licenses/by/4.0/

### Seymour et al. (2020) (`reducedorder.seymour_etal`)

Coefficients in `src/jetfuelburn/reducedorder.py`, class `seymour_etal`.

Source: Table M.7 of the Supplementary Information to Seymour, K., Held, M., Georges, G., & Boulouchos, K. (2020).
Fuel Estimation in Air Transportation: Modeling global fuel consumption for commercial aviation.
_Transportation Research Part D: Transport and Environment_, 88, 102528. https://doi.org/10.1016/j.trd.2020.102528

© 2020 The Authors. Published by Elsevier Ltd. Values transcribed as printed.

Note that the authors state:
"The fuel burn models provided in SI M shall not be used for comparing fuel efficiency and emission data between aircraft models and manufacturers."

### Montlaur et al. (2025) (`reducedorder.montlaur_etal`)

Coefficients in `src/jetfuelburn/reducedorder.py`, class `montlaur_etal`.

Source: Montlaur, A., Trapote-Barreira, C., & Delgado, L. (2025).
Analytical models of flight fuel consumption and Non-CO2 emissions as a function of aircraft capacity.
_Applied Sciences_, 15(17), 9688. https://doi.org/10.3390/app15179688

© 2025 by the authors. Licensee MDPI, Basel, Switzerland.

### Sacchi et al. (2023) (`reducedorder.sacchi_etal`)

Coefficients in `src/jetfuelburn/reducedorder.py`, class `sacchi_etal`.

Source: Sacchi, R., Becattini, V., Gabrielli, P., Cox, B., Dirnaichner, A., Bauer, C., & Mazzotti, M. (2023).
How to make climate-neutral aviation fly. _Nature Communications_, 14, 3989. https://doi.org/10.1038/s41467-023-39749-y,
and its Supplementary Data, https://doi.org/10.5281/zenodo.8059750

© The Author(s) 2023.

### Poll & Schumann (2025) aircraft parameters (`utility.aerodynamics.poll_schumann_drag_polars`)

File: `src/jetfuelburn/data/PS2025/table_2.csv`

Source: Table 2 of Poll, D.I.A., & Schumann, U. (2025).
An estimation method for the fuel burn and other performance characteristics of civil transport aircraft;
part 3 full flight profile when the trajectory is specified.
_The Aeronautical Journal_, 129(1334), 825-861. https://doi.org/10.1017/aer.2024.141

© The Author(s), 2025. Published by Cambridge University Press on behalf of Royal Aeronautical Society.
Changes: Table 2 transcribed to CSV, values as published, without the columns psi_6, (FL)_MO and M_MO;
equations re-implemented in Python.

### EMEP/EEA air pollutant emission inventory guidebook 2009 (`reducedorder.eea_emission_inventory_2009`)

File: `src/jetfuelburn/data/EEA2009/data.json` (jet aircraft: A310, A320, A330, A342, B463, B727, B731, B734, B743, B744, B757, B763, B777, BA11, DC10, DC9, F100, F28, MD81)

Source: European Environment Agency (EEA), EMEP/EEA air pollutant emission inventory guidebook 2009, Part B, chapter 1.A.3.a Aviation,
annex file `1.A.3.a Aviation vs2.3spreadsheet1.xls` (`Aviation_annex.zip`),
https://www.eea.europa.eu/en/analysis/publications/emep-eea-emission-inventory-guidebook-2009

© EEA, Copenhagen, 2009.

## Data used with permission

### FOI turboprop and military transport data (`reducedorder.eea_emission_inventory_2009`)

File: `src/jetfuelburn/data/EEA2009/data.json` (AN26, AT43, AT72, B190, B350, BE20, C130, C208, D328, DH8D, DHC3, DHC7, E110, F27, F406, F50, JS31, JS41, P3, SB20, SC7, SF34, SH33, SH36, SW4)

Source: FOI – Swedish Defence Research Agency (Totalförsvarets forskningsinstitut), Hurdy-Gurdy 1.2/1.3 calculations,
published in the annex of the EMEP/EEA guidebook 2009 as `1.A.3.a Aviation vs2.3spreadsheet2-1updated2007.xls`.

© 2001–2003 FOI, Sweden. Used with permission of FOI (email of 15 April 2026, `docs/_static/permissions/email_foi_se.pdf`).

FOI asks users to note the assumptions and interpolations documented in the spreadsheet,
and that the underlying emission data are close to 30 years old, so many newer aircraft and engine versions are not represented.

## Public-domain data

### US DOT airline statistics (`statistics.usdot`)

Files: `src/jetfuelburn/data/USDOT/USDOT_data_*.json`

Source: U.S. Department of Transportation, Bureau of Transportation Statistics (BTS), TranStats, Air Carrier Summary Data,
T2: U.S. Air Carrier Traffic and Capacity Statistics by Aircraft Type (Form 41 Schedule T-100), with the lookup table `L_AIRCRAFT_TYPE`.

### Airport codes and coordinates (`utility.geography`)

File: `src/jetfuelburn/data/Airports/airports.csv.gz`

Source: OurAirports, https://ourairports.com/data/, file `airports.csv` from https://github.com/davidmegginson/ourairports-data
