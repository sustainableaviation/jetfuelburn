# JetFuelBurn

`jetfuelburn` is a Python package for calculating fuel burn in aircraft. It is designed to be used in the context of environmental impact assessment of air travel, aircraft performance analysis and optimisation.

The package implements different fuel burn models. Some are based on basic aerodynamic equations like the [Breguet range equation](), while others are more complex and ultimately based on [EUROCONTROL BADA](https://www.eurocontrol.int/model/bada) or [Piano X](https://www.lissys.uk/index2.html) simulation data.

Extensive documentation and diagrams are provided for relevant functions. The package is designed to be used with physical units enabled by the [`pint` package](https://pint.readthedocs.io/en/stable/). This allows for straightforward conversions of both input and output values.

The package also includes helper function for basic atmospheric physics problems and the allocation of fuel burn to different cabin classes (economy, business, etc.).

<img src="https://upload.wikimedia.org/wikipedia/commons/3/33/Fuel_Quantity_Indicator_B737-300.svg" width="300">

