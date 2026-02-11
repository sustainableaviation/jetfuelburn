# Model Comparison

## Aircraft Type Coverage by Model

The following table shows which aircraft types are supported by each model in the `jetfuelburn` package:

|                                                                                                   | A220-300 | A320neo | A330-300   | A340-300 | B777-300ER | Comment                                    |
|---------------------------------------------------------------------------------------------------|----------|---------|------------|----------|------------|--------------------------------------------|
| **[US DOT Statistics (2024)][jetfuelburn.statistics.usdot]**                                     | ✓        | ✓       | ✓          | ✗        | ✓          |                                            |
| **[AIM2015][jetfuelburn.reducedorder.aim2015]**                                                  | ✗        | ✗       | ✓          | ✗        | ✓          |                                            |
| **[EEA Emission Inventory 2009][jetfuelburn.reducedorder.eea_emission_inventory_2009]**          | ✗        | ✗       | ✓*         | ✗ (A342) | ✓*         | * exact subtype not specified              |
| **[Lee et al][jetfuelburn.reducedorder.lee_etal]**                                               | ✗        | ✗       | ✗ (A332)   | ✗        | ✗ (B772)   |                                            |
| **[myclimate][jetfuelburn.reducedorder.myclimate]**                                              | ✗        | ✗       | ✓**        | ✗        | ✓**        | ** exact subtype not specified             |
| **[Seymour et al][jetfuelburn.reducedorder.seymour_etal]**                                       | ✓        | ✓       | ✓          | ✓        | ✓          |                                            |
| **[Yanto et al][jetfuelburn.reducedorder.yanto_etal]**                                           | ✗        | ✗       | ✓          | ✓        | ✓          |                                            |
| **[(Breguet) Range Equation][jetfuelburn.rangeequation]**                                                | ✓        | ✓       | ✓          | ✓        | ✓          | requires values for L/D, TSFC, etc. as input|
| **[Google's Travel Impact Model](https://github.com/google/travel-impact-model)**        | ✓        | ✓       | ✓          | ✓        | ✓          |                                            |
| **[Poll-Schumann (pycontrails)](https://py.contrails.org/notebooks/AircraftPerformance.html)**   | ✓        | ✓       | ✓          | ✓        | ✓          |                                            |

!!! note "Model Coverage"
    - ✓ indicates the aircraft type is supported by the model
    - ✗ indicates the aircraft type is not supported
    - Values in parentheses (e.g., A332, B772) indicate the closest available aircraft variant
    - This table shows a representative sample of aircraft types; most models support many more aircraft types
    - Check each model's `available_aircraft()` method for the complete list of supported aircraft

