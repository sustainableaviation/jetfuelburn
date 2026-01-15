#%%
# runs code as interactive cell 
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# sys
import os
# plotting
import matplotlib.pyplot as plt
# unit conversion
cm = 1/2.54 # for inches-cm conversion
# time manipulation
from datetime import datetime
# data science
import numpy as np
import pandas as pd

# SETUP #########################################

plt.rcParams.update({
    "font.family": "Arial",
    'font.size': 11
})

# DATA IMPORT ###################################

# DATA MANIPULATION #############################

# Define time range
years = np.arange(2000, 2042)

# Define rates based on the logic
rates = []
for y in years:
    if y < 2018:
        rates.append(-0.6)
    else:
        rates.append(-0.8)

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num='main',
    nrows=1,
    ncols=1,
    dpi=300,
    figsize=(20*cm, 7*cm), 
)

# AXIS LIMITS ################

ax.set_xlim(2000, 2040)
ax.set_ylim(-1.0, -0.4)

# TICKS AND LABELS ###########

ax.grid(True, which='both', linestyle=':', linewidth=0.6, alpha=0.6)

ax.set_ylabel('Annual Improvement Rate [%]')

# GRIDS ######################

# PLOTTING ###################

# Plot the step function segments
ax.plot(
    [2000, 2018], 
    [-0.6, -0.6], 
    linestyle='-', 
    color='b', 
    lw=2, 
    label='Historical Trend (-0.6%)'
)

ax.plot(
    [2018, 2040], 
    [-0.8, -0.8], 
    linestyle='-', 
    color='r', 
    lw=2, 
    label='Future Assumption (-0.8%)'
)

# Vertical dashed line connecting the steps (continuity)
ax.plot(
    [2018, 2018], 
    [-0.6, -0.8], 
    linestyle='--', 
    color='k', 
    lw=1
)

# Add the specific vertical dashed line at 2018 as requested
ax.axvline(
    x=2018, 
    color='black', 
    linestyle='--', 
    alpha=0.5
)

ax.text(
    2018.5, 
    -0.5, 
    ' 2018', 
    color='black', 
    verticalalignment='center'
)

# LEGEND ####################

ax.legend(loc='lower left')

# EXPORT #########################################

from pathlib import Path

figure_name = str(Path(__file__).stem + '.svg')
plt.savefig(
    fname = figure_name,
    format="svg",
    bbox_inches='tight',
    transparent = False
)