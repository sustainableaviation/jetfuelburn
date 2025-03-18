#%%
# runs code as interactive cell 
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
# unit conversion
cm = 1/2.54 # for inches-cm conversion
# time manipulation
from datetime import datetime

# data science
import numpy as np
import pandas as pd

# i/o
from pathlib import PurePath, Path

# SETUP #########################################

plt.rcParams.update({
    "font.family": "Arial",
    'font.size': 12
})

# DATA IMPORT ###################################

# DATA MANIPULATION #############################

takeoff = (0, 0)
cruise_1 = (200, 30000)
cruise_2 = (400, 30000)
destination = (600, 0)
cruise_3 = (700, 15000)
cruise_4 = (750, 15000)
alternate = (850, 0)

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num = 'main',
    nrows = 1,
    ncols = 1,
    dpi = 300,
    figsize=(20*cm, 10*cm), # A4=(210x297)mm,
    sharex=True
)

# AXIS LIMITS ################

ax.set_xlim(0, 900)
ax.set_ylim(0,32000)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis='x', which='both', bottom=True)
ax.tick_params(axis='y', which='both', bottom=True)

import matplotlib.ticker as ticker
def thousand_formatter(value, tick_number):
    """
    Formats the tick label with thousand separators: 1000 = 1'000.
    """
    return f"{int(value):,}".replace(",", "'")

ax.yaxis.set_major_formatter(ticker.FuncFormatter(thousand_formatter))

# GRIDS ######################

ax.grid(which='both', axis='y', linestyle='-', linewidth=0.5)
ax.grid(which='major', axis='x', linestyle='--', linewidth=0.5)

# AXIS LABELS ################

ax.set_ylabel("Altitude (above sea level) [ft]")
ax.set_xlabel("Distance [nmi]")

# PLOTTING ###################

# Plot points
points_main = [takeoff, cruise_1, cruise_2, destination]
x_climb, y_climb = zip(*points_main)
ax.plot(x_climb, y_climb, marker='o', linestyle='-', color='k', label='Main Segment (Fuel burned)')

points_alternate = [destination, cruise_3, cruise_4, alternate]
x_alternate, y_alternate = zip(*points_alternate)
ax.plot(x_alternate, y_alternate, marker='o', linestyle='--', color='k', label='Diversion Segment (Fuel uplifted)')

ax.plot(cruise_2[0], cruise_2[1], marker='o', linestyle='-', color='green')
ax.plot(cruise_4[0], cruise_4[1], marker='o', linestyle='-', color='green')

# ANNOTATIONS #################

ax.annotate(
    '$m_2$',
    xy=cruise_2,
    xytext=(cruise_2[0] -40, cruise_2[1] - 7000),
    arrowprops=dict(
        facecolor='black',
        shrink=0.05,
        headwidth=5,
        width=1
    ),
    fontsize=12,
    ha='center'
)

ax.annotate(
    '$m_4$',
    xy=cruise_4,
    xytext=(cruise_4[0] -40, cruise_4[1] - 7000),
    arrowprops=dict(
        facecolor='black',
        shrink=0.05,
        headwidth=5,
        width=1
    ),
    fontsize=12,
    ha='center'
)

# SHADED AREA #################

ax.axvspan(0, 200, color='blue', alpha=0.2, label='Engine Database (+Extrapolation)')
ax.axvspan(400, 700, color='blue', alpha=0.2,)
ax.axvspan(200, 400, color='red', alpha=0.2, label='Breguet')
ax.axvspan(700, 750, color='red', alpha=0.2)
ax.axvspan(750, 850, color='blue', alpha=0.2,)

# TEXT ######################

ax.text(
    0.05, 0.05, 'All flight segments highly simplified!',
    transform=ax.transAxes,
    fontsize=12,
    verticalalignment='bottom',
    horizontalalignment='left'
)


# LEGEND ####################

ax.legend(loc='upper right')

# EXPORT #########################################

figure_name: str = str(Path.cwd().stem + '.svg')

plt.savefig(
    fname = figure_name,
    format="svg",
    bbox_inches='tight',
    transparent = False
)