# Model Comparison

The `jetfuelburn` package implements multiple fuel burn calculation models, each with different levels of complexity, data requirements, and accuracy. This page provides a comprehensive comparison to help you choose the most appropriate model for your use case.

## Aircraft Type Coverage by Model

The following table shows which aircraft types are supported by each model in the `jetfuelburn` package:

|                                                               |A220-300 |A320neo  |A330-300 |A340-300 |B777-300ER| Comment   |
|---------------------------------------------------------------|---------|--------|--------|--------|----------|------------------------------------------|
| **[US DOT Statistics (2024)][jetfuelburn.statistics.usdot]**  |✓        |✓        |✓        |✗        |✓          |                                           |
| **aim2015**                    |✗        |✗        |✓        |✗        |✓          |                                           |
| **EEA Emission Inventory 2009**|✗        |✗        |✓*       |✗        |✓*         |* exact subtype not specified             |
| **[Lee et al][jetfuelburn.reducedorder.lee_etal]**  |✗        |✗        |✗ (A332)|✗        |✗ (B772)   |                                           |
| **Myclimate**                  |✗        |✗        |✓**      |✗        |✓**        |** exact subtype not specified           |
| **Seymour et al**              |✓        |✓        |✓        |✓        |✓          |                                           |
| **Yanto et al**                |✗        |✗        |✗        |✗        |✗ (B773)   |                                           |
| **Breguet Range Equation**     |✓        |✓        |✓        |✓        |✓          |→ needs estimate values for L/D, TSFC, etc.|
| **Google's Travel Impact Model**|✓        |✓        |✓        |✓        |✓          |                                           |
| **Poll-Schumann (pycontrails)**|✓        |✓        |✓        |✓        |✓          |                                           |

!!! note "Model Coverage"
    - ✓ indicates the aircraft type is supported by the model
    - ✗ indicates the aircraft type is not supported
    - Values in parentheses (e.g., A332, B772) indicate similar but different aircraft variants
    - This table shows a representative sample of aircraft types; most models support many more aircraft types
    - Check each model's `available_aircraft()` method for the complete list of supported aircraft

