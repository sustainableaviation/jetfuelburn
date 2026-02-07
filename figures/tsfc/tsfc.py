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

# Dimensionless thrust (normalized by max thrust)
T_hat = np.linspace(0.3, 1.0, 300)

# Dimensionless TSFC curves (normalized by reference TSFC)
TSFC_hat_M07 = 1.00 + 0.35 * (T_hat - 0.55)**2
TSFC_hat_M08 = 1.08 + 0.40 * (T_hat - 0.65)**2
TSFC_hat_M09 = 1.18 + 0.45 * (T_hat - 0.75)**2

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

ax.set_xlim(0.25, 1.2)
#ax.set_ylim(OEW, 300)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis='x', which='minor', bottom=True)

ax.tick_params(
    axis='both', 
    which='both', 
    bottom=True, 
    top=False, 
    labelbottom=False, 
    labelleft=False
)

# GRIDS ######################

ax.grid(which='major', axis='y', linestyle='-', linewidth = 0.5)
ax.grid(which='minor', axis='y', linestyle=':', linewidth = 0.5)
ax.grid(which='major', axis='x', linestyle='-', linewidth = 0.5)
ax.grid(which='minor', axis='x', linestyle=':', linewidth = 0.5)

# axes[0]IS LABELS ################

ax.set_xlabel('Thrust (force, eg. [N])')
ax.set_ylabel("TSFC (time/length, eg. [mg/Ns])")

# PLOTTING ###################

ax.plot(T_hat, TSFC_hat_M07, label='M=0.7')
ax.plot(T_hat, TSFC_hat_M08, label='M=0.8')
ax.plot(T_hat, TSFC_hat_M09, label='M=0.9')

# LEGEND ####################

ax.text(
    1.02,
    TSFC_hat_M07[-1],
    r"$M = 0.7$",
    va="center"
)

ax.text(
    1.02,
    TSFC_hat_M08[-1],
    r"$M = 0.8$",
    va="center"
)

ax.text(
    1.02,
    TSFC_hat_M09[-1],
    r"$M = 0.9$",
    va="center"
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