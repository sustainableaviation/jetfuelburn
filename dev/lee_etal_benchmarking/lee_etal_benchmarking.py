#%%
# runs code as interactive cell 
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# plotting
import matplotlib.pyplot as plt
# unit conversion
cm = 1/2.54 # for inches-cm conversion
# time manipulation
from datetime import datetime
# data science
import numpy as np
import pandas as pd

from jetfuelburn.reducedorder import lee_etal
import pint_pandas
pint_pandas.PintType.ureg.setup_matplotlib()
from jetfuelburn import ureg

# SETUP #########################################

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Arial",
    "font.sans-serif": "Computer Modern",
    'font.size': 11
})

# DATA IMPORT ###################################

# Read CSV data
df_fres_const = pd.read_csv(
    filepath_or_buffer='data/fres_0-08.csv',
    header=0,
    index_col=None
)
df_fres_dist_time = pd.read_csv(
    filepath_or_buffer='data/fres_100nmi+45min.csv',
    header=0,
    index_col=None
)
df_fres_time = pd.read_csv(
    filepath_or_buffer='data/fres_45min.csv',
    header=0,
    index_col=None
)

# DATA MANIPULATION #############################

input_data = {
    'acft':'B732',
    'W_E': 265825*ureg.N,
    'W_MPLD': 156476*ureg.N,
    'W_MTO': 513422*ureg.N,
    'W_MF': 142365*ureg.N,
    'S': 91.09*ureg.m ** 2,
    'C_D0': 0.0214,
    'C_D2': 0.0462,
    'c': (2.131E-4)/ureg.s,
    'h': 9144*ureg.m,
    'V': 807.65*ureg.kph,
}

results = []
for range in df_fres_const['range']:
    dict_results = lee_etal.calculate_fuel_consumption(
        acft=input_data['acft'],
        W_E=input_data['W_E'],
        W_MPLD=input_data['W_MPLD'],
        W_MTO=input_data['W_MTO'],
        W_MF=input_data['W_MF'],
        S=input_data['S'],
        C_D0=input_data['C_D0'],
        C_D2=input_data['C_D2'],
        c=input_data['c'],
        h=input_data['h'],
        V=input_data['V'],
        d=range * ureg.nmi  # Assuming range is in nautical miles
    )
    results.append({
        'range': range,
        'payload': dict_results['mass_payload']
    })

df_results = pd.DataFrame(results).pint.convert_object_dtype()


# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num = 'main',
    nrows = 1,
    ncols = 1,
    dpi = 300,
    figsize=(15*cm, 10*cm), # A4=(210x297)mm,
)

# AXIS LIMITS ################

#ax.set_xlim(1950, 2023)
#ax.set_ylim(10,30)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis='x', which='minor', bottom=True)

# GRIDS ######################

ax.grid(which='major', axis='y', linestyle='-', linewidth = 0.5)
ax.grid(which='minor', axis='y', linestyle=':', linewidth = 0.5)

ax.grid(which='major', axis='x', linestyle='-', linewidth = 0.5)
ax.grid(which='minor', axis='x', linestyle=':', linewidth = 0.5)


# AXIS LABELS ################

ax.set_ylabel("Payload [lbs]")
ax.set_xlabel("Range [nmi]")


# PLOTTING ###################

ax.plot(
    df_fres_const['range'],
    df_fres_const['payload'],
    color = 'red',
    linewidth = 1,
    marker='o',
    linestyle = '-',
    label = 'Fig. 6 in Lee et al. (f$_{res}$=0.08)'
)
"""
ax.plot(
    df_fres_dist_time['range'],
    df_fres_dist_time['payload'],
    color = 'green',
    linewidth = 1,
    marker='s',
    linestyle = '-',
    label = '100nmi+45min'
)

ax.plot(
    df_fres_time['range'],
    df_fres_time['payload'],
    color = 'blue',
    linewidth = 1,
    marker='s',
    linestyle = '-',
    label = '45min'
)
"""
ax.plot(
    df_results['range'],
    df_results['payload'].pint.to('lbs'),
    color = 'black',
    linewidth = 1,
    marker='x',
    linestyle = '-',
    label = 'My Implementation (f$_{res}$=0.08)'
)



# LEGEND ####################

ax.legend(
    loc = 'lower left',
    fontsize = 12
)


# EXPORT #########################################

from pathlib import Path

figure_name: str = Path.cwd().stem + '.pdf'
plt.savefig(
    fname = figure_name,
    format="pdf",
    bbox_inches='tight',
    transparent = False
)