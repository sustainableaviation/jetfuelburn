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
    'font.size': 12
})

# DATA IMPORT ###################################

# DATA MANIPULATION #############################

data = np.array([
    [0,0],
    [54, 136],
    [145, 10724],
    [254, 19140],
    [327, 23484],
    [400, 26200], #TOC
    [550, 26200],
    [650, 27000],
    [850, 27000],
    [950, 27800],
    [1100, 27800], #TOD
    [1213, 22127],
    [1345, 7738],
    [1444, 0],
    [1516, 0]
])

x = data[:, 0]
y = data[:, 1]


# FIGURE ########################################

# SETUP ######################

fig, (ax1, ax2) = plt.subplots(
    num='main',
    nrows=1,
    ncols=2,
    dpi=300,
    figsize=(20*cm, 7*cm),  # Adjusted for two figures side by side
    gridspec_kw={'wspace': 0.1}
)

# AXIS LIMITS ################

ax2.set_xlim(0, 1500)
ax1.set_xlim(0, 2000)
ax1.set_ylim(0, 50)

# TICKS AND LABELS ###########

ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

ax2.yaxis.tick_right()

ax2.set_xlabel('Distance [km]')
ax2.yaxis.set_label_position("right")
ax2.set_ylabel('Altitude (FL)')
yticks = [0,5000,10000,15000,20000,25000,30000]
ax2.set_yticks(yticks)
ax2.set_yticklabels([int(tick) // 100 for tick in yticks])

# GRIDS ######################

# AXIS LABELS ################

ax1.set_xlabel('Distance [km]')
ax1.set_ylabel('Fuel Burn [t]')
ax1.set_title('Data Points', fontsize=12, fontweight='bold')
ax2.set_title('Flight Profile (fixed distance+payload)', fontsize=12, fontweight='bold')

# PLOTTING ###################

bbox = ax2.get_position()

# Line from bottom right of ax2 to target point
line1 = plt.Line2D(
    [bbox.x1, 0.15],  # Changed from bbox.x0 to bbox.x1
    [bbox.y0, 0.25],
    transform=fig.transFigure,
    color="red",
    linewidth=1,
    linestyle="--"
)
fig.add_artist(line1)

# Line from top right of ax2 to target point
line2 = plt.Line2D(
    [bbox.x1, 0.15],  # Changed from bbox.x0 to bbox.x1
    [bbox.y1, 0.25],
    transform=fig.transFigure,
    color="red",
    linewidth=1,
    linestyle="--"
)
fig.add_artist(line2)

# Optional: Adjust text position
text_x = 0.4
text_y = 0.24
fig.text(
    text_x, text_y,
    'single points only',
    ha='center', va='center',
    rotation=-4,
    color='black',
    fontsize=12
)

ax1.plot(0.15, 0.25, 'ro', transform=fig.transFigure)
ax1.plot(0.2, 0.31, 'ro', transform=fig.transFigure)
ax1.plot(0.25, 0.38, 'ro', transform=fig.transFigure)
ax1.plot(0.31, 0.48, 'ro', transform=fig.transFigure)
ax1.plot(0.36, 0.58, 'ro', transform=fig.transFigure)

# Generate data for ax1
x1 = np.linspace(0, 2000, 100)
y1 = 5 * np.exp(0.0005 * x1)
ax1.plot(x1, y1, linestyle='-', color='white')

ax2.plot(
    x,
    y,
    linestyle='-',
    color='k'
)

ax2.axvspan(
    0,
    1500, 
    color='orange', 
    alpha=0.2
)

# LEGEND ####################

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='orange', edgecolor='orange', alpha=0.2, label='PianoX'),
]
ax2.legend(handles=legend_elements, loc='lower left')

# EXPORT #########################################

from pathlib import Path
from matplotlib.patches import Patch
figure_name: str = str(Path(__file__).stem + '.svg')

plt.savefig(
    fname = figure_name,
    format="svg",
    bbox_inches='tight',
    transparent = False
)