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

# https://en.wikipedia.org/wiki/Airbus_A350#Specifications
OEW = 142.4

# https://www.airbus.com/sites/g/files/jlcbta136/files/2021-11/Airbus-Commercial-Aircraft-AC-A350-900-1000.pdf
point_a = (500,54+OEW)
point_b = (5830,54+OEW)
point_c = (8575, 25+OEW)
point_d = (9620,0+OEW)
point_a_325pax = (500, 30.5+OEW)
point_b_325pax = (8050, 30.5+OEW)

point_fuel_1 = (5830, 280)
point_fuel_2 = (8575, 280)
point_fuel_3 = (9620, 280-(54-25))

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num = 'main',
    nrows = 1,
    ncols = 1,
    dpi = 300,
    figsize=(20*cm, 10*cm), # A4=(210x297)mm,
)

# AXIS LIMITS ################

ax.set_xlim(500, 10000)
ax.set_ylim(OEW, 300)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis='x', which='minor', bottom=True)

import matplotlib.ticker as ticker
def thousand_formatter(value, tick_number):
    """
    Formats the tick label with thousand separators: 1000 = 1'000.
    """
    return f"{int(value):,}"#.replace(",", "'")

ax.xaxis.set_major_formatter(ticker.FuncFormatter(thousand_formatter))

# Manually set the x-ticks from a list
x_ticks = [500, 2000, 4000, 6000, 8000, 10000]
ax.set_xticks(x_ticks)


# Get current y-ticks
y_ticks = ax.get_yticks()
y_tick_labels = [f"{tick:.0f}" for tick in y_ticks]  # Convert ticks to strings


# Manually set the y-ticks
y_ticks = [OEW, 160, 180, 200, 220, 240, 260, 280, 300]
ax.set_yticks(y_ticks)

# Modify the lowest y-tick label
y_tick_labels[0] = r"OEW$\sim$142"
# Set the modified labels
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_tick_labels)


# GRIDS ######################

ax.grid(which='major', axis='y', linestyle='-', linewidth = 0.5)
ax.grid(which='minor', axis='y', linestyle=':', linewidth = 0.5)
ax.grid(which='major', axis='x', linestyle='-', linewidth = 0.5)
ax.grid(which='minor', axis='x', linestyle=':', linewidth = 0.5)

# axes[0]IS LABELS ################

ax.set_xlabel('Range [NM]')
ax.set_ylabel("Weight [t]")
ax.yaxis.set_label_coords(-0.07, 0.5)

# PLOTTING ###################

plt.plot(
    [point_a[0], point_b[0], point_c[0], point_d[0]],
    [point_a[1], point_b[1], point_c[1], point_d[1]],
    color = 'black',
    linestyle = '-',
    linewidth = 1,
    marker = 'o',
    label = 'Max. Structural Payload',
)
plt.plot(
    [point_a[0], point_fuel_1[0], point_fuel_2[0], point_fuel_3[0]],
    [point_a[1], point_fuel_2[1], point_fuel_2[1], point_fuel_3[1]],
    color = 'black',
    linestyle = '--',
    linewidth = 1,
    label='Total Weight (incl. Fuel)'
)

# Add a horizontal line at 280
ax.axhline(y=280, color='red', linestyle='-', linewidth=2, label='MTOW')

ax.annotate(
    'A',
    xy = point_a,
    xytext = (point_a[0]+100, point_a[1]+7),
    fontsize = 12,
)
ax.annotate(
    'B',
    xy = point_b,
    xytext = (point_b[0]+100, point_b[1]+2),
    fontsize = 12,
)
ax.annotate(
    'C',
    xy = point_c,
    xytext = (point_c[0]+100, point_c[1]+2),
    fontsize = 12,
)
ax.annotate(
    'D',
    xy = point_d,
    xytext = (point_d[0]+100, point_d[1]+2),
    fontsize = 12,
)

ax.fill_between(
    x = [point_a[0], point_b[0]],
    y1 = [point_a[1], point_b[1]],
    y2 = 0,
    color = 'tab:blue',
    alpha = 0.35,
    label = 'Max. Payload',
)
ax.fill_between(
    x = [point_b[0], point_c[0]],
    y1 = [point_b[1], point_c[1]],
    y2 = 0,
    color = 'tab:orange',
    alpha = 0.35,
    label = 'Fuel/Payload Tradeoff',
)
ax.fill_between(
    x = [point_c[0], point_d[0]],
    y1 = [point_c[1], point_d[1]],
    y2 = 0,
    color = 'tab:red',
    alpha = 0.35,
    label = 'Payload/Range Tradeoff',
)

ax.annotate(
    '',
    xy=point_b,
    xytext=point_fuel_1,
    arrowprops=dict(arrowstyle='<->', color='black', lw=1),
)

mid_x = (point_b[0] + point_fuel_1[0]) / 2
mid_y = (point_b[1] + point_fuel_1[1]) / 2
ax.text(mid_x - 200, mid_y-9, 'Fuel at max. \n Payload Efficiency', ha='right', fontsize=12)

ax.annotate(
    '',
    xy=point_c,
    xytext=point_fuel_2,
    arrowprops=dict(arrowstyle='<->', color='black', lw=1),
)

mid_x_2 = (point_c[0] + point_fuel_2[0]) / 2
mid_y_2 = (point_c[1] + point_fuel_2[1]) / 2
ax.text(mid_x_2 - 200, mid_y_2+7, 'Max. Fuel', ha='right', fontsize=12)


# LEGEND ####################

ax.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.25),
    ncol=3,
)

# EXPORT #########################################

from pathlib import Path
figure_name: str = str(Path(__file__).stem + '.svg')

plt.savefig(
    fname = figure_name,
    format="svg",
    bbox_inches='tight',
    transparent = False
)