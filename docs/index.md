# JetFuelBurn

[![PyPI Downloads](https://img.shields.io/pypi/dm/jetfuelburn?label=PyPI%20Downloads&logo=pypi&logoColor=white)](https://pypistats.org/packages/jetfuelburn)
[![License: MIT](https://img.shields.io/pypi/l/jetfuelburn?label=License&logo=open-source-initiative&logoColor=white)](https://pypi.org/project/jetfuelburn/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jetfuelburn?logo=python&logoColor=white)](https://pypi.org/project/jetfuelburn/)
[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)
![Coverage](https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/badges/coverage.svg)

`jetfuelburn` is a Python package for calculating fuel burn in aircraft. It is designed to be used in the context of environmental impact assessment of air travel. It includes helper function for basic atmospheric physics and the allocation of fuel burn to different cabin classes.

The package implements models from textbooks and scientific publications. Some are based on basic aerodynamic equations like the [Breguet range equation](https://en.wikipedia.org/wiki/Range_(aeronautics)), while others are more complex and ultimately based on [EUROCONTROL BADA](https://www.eurocontrol.int/model/bada) or [Piano X](https://www.lissys.uk/index2.html) simulation data.

```python exec="true" html="true"
import csv
import plotly.express as px

data = {'Range (km)': [], 'Value': [], 'Aircraft': []}
with open('docs/_static/figure_data/usdot_fuel_burn.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        for aircraft in ['A320', 'B737', 'A330', 'B757', 'A350', 'B787']:
            data['Range (km)'].append(int(row['Range (km)']))
            data['Value'].append(float(row[aircraft]))
            data['Aircraft'].append(aircraft)

fig = px.line(
    x=data['Range (km)'],
    y=data['Value'],
    color=data['Aircraft'],
    labels={'x': 'Range at average Payload [km]', 'y': 'Fuel Burn per Seat [kg]', 'color': 'Aircraft Type'},
)

fig.add_layout_image(
    dict(
        source="https://upload.wikimedia.org/wikipedia/commons/a/ae/Airbus_A320_clipart.svg",
        xref="paper", # reference to the paper (plot area) coordinates
        yref="paper", # reference to the paper (plot area) coordinates
        x=0.02,
        y=0.98,
        sizex=0.55,
        sizey=0.55,
        xanchor="left",
        yanchor="top",
        layer="above"
    )
)

print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
# https://pawamoy.github.io/markdown-exec/gallery/#with-plotly
```
_Interactive visualization of fuel burn for different Airbus and Boeing aircraft types, based on 2018 statistical data provided by the U.S. Department of Transportation ([`jetfuelburn.statistics.usdot`][])._