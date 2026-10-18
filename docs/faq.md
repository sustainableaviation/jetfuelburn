# FAQ

## EUROCONTROL BADA License

Q: Was Eurocontrol BADA model data used in developing (parts of) the JetFuelBurn Python package?

!!! note
    [Base of Aircraft Data (BADA)](https://www.eurocontrol.int/model/bada) is an aircraft performance model (APM) developed and maintained by the [European Organisation for the Safety of Air Navigation (Eurocontrol)](https://en.wikipedia.org/wiki/Eurocontrol). The BADA model data is proprietary and requires a valid license for use. In addition, license terms restrict the use of BADA in various ways.

A: **No, not directly**.

The [reduced order](api/reducedorder.md) module of the JetFuelBurn package implements three regression models which were in part developed based on BADA data. However, no BADA model data was used in developing any part of the JetFuelBurn package itself. 

### Model Overview

| Model |  Publication Year | Disclaimer/Limitations |
|-------|-------------------|------------------------|
| [`jetfuelburn.reducedorder.lee_etal`][] | 2010 | None |
| [`jetfuelburn.reducedorder.yanto_etal`][] | 2017 | None |
| [`jetfuelburn.reducedorder.seymour_etal`][] | 2020 | Yes: `The fuel burn models provided (...) shall not be used for comparing fuel efficiency and emission data between aircraft models and manufacturers.` |

### Seymour et al. Model Disclaimer

The [`jetfuelburn.reducedorder.seymour_etal`][] model for fuel burn estimation of commercial aircraft is a reduced order model. This means that the model is based on statistical analysis (regression) of a more complex model. In this specific case, Seymour et al. used a combination of BADA and ICAO Engine Emissions Databank data to compute high-resolution fuel burn estimates.

Having computed many such high-resolution estimates for different routes, they then performed a regression analysis to derive a reduced order model that can be used to compute fuel burn estimates with much lower computational effort. Their regression has the great-circle distance $R$ between origin and destination as its only variable, since they assume an average payload per aircraft:
$$
F=a_1 \cdot R^2 + a_2 \cdot R + c
$$
While Seymour et al. in developing their reduced-order model therefore used proprietary BADA data under license, the resulting regression coefficients \(a_1\), \(a_2\), and \(c\) have been published in Table M.7 of the Supplementary Information to their open-access peer-reviewed article (CC BY 4.0). JetFuelBurn uses the coefficients as printed in Table M.7.

Note, however, that in the disclaimer section of their article, they mention that:

> This document has been created with elements of Base of Aircraft Data (BADA) Family 3 Release 3.15
> which has been made available by EUROCONTROL to ETH Zurich (...). EUROCONTROL has all relevant rights to BADA.
> (...) The fuel burn models provided in SI M [Section M of the Supplementary Information, which holds Table M.7]
> shall not be used for comparing fuel efficiency and emission data between aircraft models and manufacturers.
> Recommended model applications are reported in Section 3.5.

This disclaimer covers Table M.7 and therefore the coefficients used by JetFuelBurn. This notice is included with the implementation of the Seymour et al. model in the JetFuelBurn package.