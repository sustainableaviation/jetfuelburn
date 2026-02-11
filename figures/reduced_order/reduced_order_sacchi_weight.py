# %%
# %%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# sys
import os
from pathlib import Path

# plotting
import matplotlib.pyplot as plt

# unit conversion
cm = 1 / 2.54  # for inches-cm conversion

# data science
import numpy as np

# SETUP #########################################

plt.rcParams.update({"font.family": "Arial", "font.size": 11})

# DATA MANIPULATION #############################

# Define variable range (Seating Capacity)
pax_max = np.linspace(0, 1000, 100)

# Calculate OEW (Operational Empty Weight)
# Formula: OEW = 0.0927 * pax_max^2 + 253.6 * pax_max
# Note: Decay factor removed as requested
oew_kg = 0.0927 * pax_max**2 + 253.6 * pax_max

# Convert to metric tons
oew_tons = oew_kg / 1000

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num="main",
    nrows=1,
    ncols=1,
    dpi=300,
    figsize=(20 * cm, 7 * cm),  # Adjusted height to match original image aspect ratio
)

# AXIS LIMITS ################

ax.set_xlim(0, 1000)
ax.set_ylim(0, 350)

# TICKS AND LABELS ###########

ax.set_xlabel("Maximum Seating Capacity")
ax.set_ylabel("Operational Empty Weight [t]")

# GRIDS ######################

ax.grid(True, which="both", linestyle=":", linewidth=0.6, alpha=0.6)

# PLOTTING ###################

# Plot the model result
ax.plot(pax_max, oew_tons, linestyle="-", color="r", lw=2, label="Model result")

# LEGEND ####################


# EXPORT #########################################

# Note: __file__ is defined when running as a script, but might fail in
# interactive window depending on configuration.
try:
    filename = Path(__file__).stem
except NameError:
    filename = "aircraft_oew_plot"

figure_name = str(filename + ".svg")

plt.savefig(fname=figure_name, format="svg", bbox_inches="tight", transparent=False)

plt.show()
