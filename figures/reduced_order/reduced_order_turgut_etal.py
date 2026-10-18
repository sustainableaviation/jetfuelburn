# %%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch, Patch

# unit conversion
cm = 1 / 2.54  # for inches-cm conversion

# data science
import numpy as np

# file paths
from pathlib import Path

# SETUP #########################################

plt.rcParams.update(
    {
        "text.usetex": False,
        "font.family": "sans-serif",
        "font.sans-serif": "Arial",
        "font.size": 12,
    }
)

# DATA ##########################################

# Three cruise levels, spaced so each one lands on a separate point
# of the regression. The short ramps between them are the step climbs.
CRUISE_LEVELS = (
    # flight level, segment start [km], segment end [km], color
    (270, 400, 550, "#0072B2"),
    (310, 650, 850, "#CC79A7"),
    (350, 950, 1100, "#D55E00"),
)
TOC_KM = CRUISE_LEVELS[0][1]
TOD_KM = CRUISE_LEVELS[-1][2]

profile = np.array(
    [
        [0, 0],
        [54, 136],
        [145, 10724],
        [254, 19140],
        [327, 23484],
        [400, 27000],
        [550, 27000],
        [650, 31000],
        [850, 31000],
        [950, 35000],
        [1100, 35000],
        [1213, 23000],
        [1345, 8000],
        [1444, 0],
        [1516, 0],
    ]
)
x_profile = profile[:, 0]
y_profile = profile[:, 1]

# Table 2 of Turgut et al. (2014), Boeing 737-800.
# FF [kg/h] = C0 + Ch*h[ft] + Cm*m[t] + CV*V[kt].
B738 = {
    "constant": -708.506,
    "altitude": -0.024,
    "mass": 16.633,
    "tas": 7.289,
}
TAS_KT = 364.0
MASS_REF_T = 60.3


def fuel_flow_kg_per_h(altitude_ft, mass_t, tas_kt=TAS_KT):
    return (
        B738["constant"]
        + B738["altitude"] * altitude_ft
        + B738["mass"] * mass_t
        + B738["tas"] * tas_kt
    )


# A lighter mass stays left of the reference line, so the cruise-level
# connectors meet the 60.3 t line without crossing another fit.
MASS_LINES = (
    (MASS_REF_T, "60.3 t", "black", 2.0, "-"),
    (45.0, "45 t", "0.45", 1.15, "--"),
)
fl = np.linspace(220, 400, 120)

# FIGURE ########################################

fig, (ax1, ax2) = plt.subplots(
    num="main",
    nrows=1,
    ncols=2,
    dpi=300,
    figsize=(20 * cm, 7 * cm),
    gridspec_kw={"wspace": 0.1},
)

# LEFT: multiple linear regression ################
# Altitude shares the vertical scale with the flight profile, so each
# cruise level meets its fuel-flow point on a horizontal line.
# Fuel flow falls with altitude and rises with mass. TAS is held
# at the paper's mean cruise speed, so the third regressor is fixed.

for mass_t, label, color, lw, ls in MASS_LINES:
    ax1.plot(
        fuel_flow_kg_per_h(fl * 100, mass_t),
        fl,
        color=color,
        linewidth=lw,
        linestyle=ls,
        label=label,
        zorder=2,
    )

ax1.set_xlim(1600, 2900)
ax1.set_ylim(0, 420)
ax1.set_xlabel("Fuel Flow [kg/h]")
ax1.set_ylabel("Altitude (FL)")
ax1.set_title("Linear Regression", fontsize=12, fontweight="bold")
ax1.grid(True, which="major", linestyle="--", linewidth=0.5)
ax1.set_axisbelow(True)
ax1.set_yticks([0, 100, 200, 300, 400])

legend1 = ax1.legend(
    loc="lower left",
    framealpha=0.95,
    handlelength=1.8,
    handletextpad=0.4,
    borderpad=0.3,
    labelspacing=0.2,
)
legend1.set_zorder(6)

# RIGHT: cruise segment only #####################

ax2.axvspan(TOC_KM, TOD_KM, color="#009E73", alpha=0.22, zorder=0)
ax2.plot(x_profile, y_profile, linestyle="-", color="k", zorder=2)

ax2.set_xlim(0, 1500)
ax2.set_ylim(0, 42000)
ax2.grid(True, which="both", linestyle="--", linewidth=0.5)
ax2.set_axisbelow(True)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")
ax2.set_xlabel("Distance [km]")
ax2.set_ylabel("Altitude (FL)")
yticks = [0, 10000, 20000, 30000, 40000]
ax2.set_yticks(yticks)
ax2.set_yticklabels([int(tick) // 100 for tick in yticks])
ax2.set_title("Flight Profile", fontsize=12, fontweight="bold")

legend2 = ax2.legend(
    handles=[
        Patch(
            facecolor="#009E73", edgecolor="#009E73", alpha=0.22, label="Cruise (FDR)"
        ),
    ],
    loc="lower left",
    framealpha=0.95,
)
legend2.set_zorder(6)

# LINK ###########################################
# Each cruise level is one (altitude, mass, TAS) sample. Mass and TAS
# stay at the B738 mean, so the three samples sit on the 60.3 t line.

for fl_level, x0, x1, color in CRUISE_LEVELS:
    altitude_ft = fl_level * 100
    ff = fuel_flow_kg_per_h(altitude_ft, MASS_REF_T)
    ax2.plot(
        [x0, x1],
        [altitude_ft, altitude_ft],
        color=color,
        linewidth=2.4,
        solid_capstyle="butt",
        zorder=3,
    )
    ax1.plot(
        ff,
        fl_level,
        marker="o",
        color=color,
        markersize=7,
        linestyle="None",
        markeredgecolor="white",
        markeredgewidth=0.6,
        zorder=5,
    )
    fig.add_artist(
        ConnectionPatch(
            xyA=(x0, altitude_ft),
            coordsA=ax2.transData,
            xyB=(ff, fl_level),
            coordsB=ax1.transData,
            linestyle="--",
            linewidth=1.0,
            color=color,
            zorder=4,
        )
    )

# EXPORT #########################################

figure_name = str(Path(__file__).stem + ".svg")
plt.savefig(fname=figure_name, format="svg", bbox_inches="tight", transparent=False)
# %%
