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
ax1.set_ylim(0, 150)

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

# PLOTTING ###################

ax2.plot(
    x,
    y,
    #marker='o',
    linestyle='-',
    color='k'
)

ax2.axvspan(
    0,
    1500, 
    color='purple', 
    alpha=0.2
)

# Sample data for color field
x_field = np.linspace(0, 5000, 100)
y_field = np.linspace(0, 300, 100)
X, Y = np.meshgrid(x_field, y_field)
Z = np.sin(X / 3000) * np.sin(Y / 100)

# Plotting the color field
c = ax1.pcolormesh(X, Y, Z, shading='auto', cmap='viridis')

# Adding color bar
fig.colorbar(c, ax=ax1, orientation='vertical', pad=0.3, fraction=0.05, location='left', label='Fuel Burn').ax.set_yticklabels([])

# Setting labels
ax1.set_xlabel('Distance [km]')
ax1.set_ylabel('Max. Seats [1]')
ax1.set_title('Multi-Variate Simulation', fontsize=12, fontweight='bold')
ax2.set_title('Flight Profile (fixed distance+payload)', fontsize=12, fontweight='bold')

# Drawing a line from the lower right corner of ax2 into the middle of ax1
bbox = ax2.get_position()
line = plt.Line2D(
    [bbox.x0, 0.31],  # x-coordinates in axes fraction
    [bbox.y0, 0.2],  # y-coordinates in axes fraction
    transform=fig.transFigure,
    color="red",
    linewidth=1,
    linestyle="--"
)
fig.add_artist(line)

bbox = ax2.get_position()
line = plt.Line2D(
    [bbox.x0, 0.31],  # x-coordinates in axes fraction
    [bbox.y1, 0.2],  # y-coordinates in axes fraction
    transform=fig.transFigure,
    color="red",
    linewidth=1,
    linestyle="--"
)
fig.add_artist(line)

# Adding text along the line
fig.text(
    (bbox.x0 + 0.21) / 2,  # x-coordinate in figure fraction
    (bbox.y1 + 0.05) / 2,  # y-coordinate in figure fraction
    'approx. through polynomial',  # Text to display
    ha='center',  # Horizontal alignment
    va='center',  # Vertical alignment
    rotation=47,  # Rotation angle
    color='white',  # Text color
    fontsize=12  # Font size
)

# Adding a point at (0.35, 0.2) in figure coordinates
ax1.plot(0.31, 0.2, 'ro', transform=fig.transFigure)

# LEGEND ####################


from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='purple', edgecolor='purple', alpha=0.2, label='Eurocontrol IMPACT'),
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
# %%
