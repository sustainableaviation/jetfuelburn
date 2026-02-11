# %%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, ConnectionPatch
import numpy as np
from pathlib import Path

# SETUP #########################################

cm = 1 / 2.54
plt.rcParams.update({"font.family": "Arial", "font.size": 12})

# DATA GENERATION ###############################

# --- Left Plot Data ---
np.random.seed(42)
# Reduced points by half (approx 22)
weights_sim = np.random.uniform(5, 330, 22)
slopes_sim = 0.064 * weights_sim + 0.5 + np.random.normal(0, 0.8, 22)

# Linear Fit
m, c = np.polyfit(weights_sim, slopes_sim, 1)
x_fit = np.linspace(0, 350, 100)
y_fit = m * x_fit + c

# Define 4 Vertical Line Positions with decreasing distances
vline_x = [200, 216, 220]

# --- Right Plot Data (Flight Profile) ---
data = np.array(
    [
        [0, 0],
        [54, 136],
        [145, 10724],
        [254, 19140],
        [327, 23484],
        [400, 26200],
        [550, 26200],
        [650, 27000],
        [850, 27000],
        [950, 27800],
        [1100, 27800],
        [1213, 22127],
        [1345, 7738],
        [1444, 0],
        [1516, 0],
    ]
)
x_prof = data[:, 0]
y_prof = data[:, 1]

# FIGURE ########################################

fig, (ax1, ax2) = plt.subplots(
    num="main",
    nrows=1,
    ncols=2,
    dpi=300,
    figsize=(20 * cm, 7 * cm),
    gridspec_kw={"wspace": 0.1},
)

# PLOT AX1 (Left) ###############################

# 1. Scatter Data
ax1.scatter(
    weights_sim,
    slopes_sim,
    s=50,
    c="#4C72B0",
    label="EMEP Data",
    edgecolor="white",
    linewidth=0.5,
    zorder=2,
)

# 2. Fit Line
ax1.plot(x_fit, y_fit, color="#55A868", linewidth=2, label="Fit", zorder=1)

# 3. Reference Lines (Vertical & Horizontal)
for vx in vline_x:
    vy = m * vx + c

    # Vertical line (Black, Dashed)
    ax1.vlines(
        x=vx, ymin=0, ymax=vy, colors="black", linestyles="--", linewidth=1, zorder=0
    )

    # Horizontal line (Red, Dashed)
    ax1.hlines(
        y=vy, xmin=0, xmax=vx, colors="red", linestyles="--", linewidth=1, zorder=0
    )

    # Intersection dot
    ax1.plot(vx, vy, "o", color="black", markersize=4, zorder=3)

# Formatting AX1
ax1.set_title("Fuel Burn Approximation", fontsize=12, fontweight="bold")
ax1.set_xlabel("Aircraft Operating Weight [t]")
ax1.set_ylabel("Fuel Weight [t]")
ax1.set_xlim(0, 350)
ax1.set_ylim(bottom=0)
ax1.grid(True, which="both", linestyle="-", linewidth=0.5, alpha=0.7)

ax1.text(
    0.12,
    0.7,
    "Iterative Solution",
    transform=ax1.transAxes,
    va="top",
    ha="left",
)

# set origin (data coords on ax1) and destination (axes fraction for text)
destination = (160, 2)  # (x, y) in ax1 data coordinates
origin = (220, 2)  # (x, y) in axes fraction for annotation text

ax1.annotate(
    "",
    xy=origin,
    xycoords="data",
    xytext=destination,
    arrowprops=dict(arrowstyle="->", color="black", linewidth=1.2),
)

# PLOT AX2 (Right) ##############################

ax2.set_xlim(0, 1500)
ax2.grid(True, which="both", linestyle="--", linewidth=0.5)
ax2.yaxis.tick_right()
ax2.set_xlabel("Distance [km]")
ax2.yaxis.set_label_position("right")
ax2.set_ylabel("Altitude (FL)")

yticks = [0, 5000, 10000, 15000, 20000, 25000, 30000]
ax2.set_yticks(yticks)
ax2.set_yticklabels([int(tick) // 100 for tick in yticks])

# Profile Line
ax2.plot(x_prof, y_prof, linestyle="-", color="k")

# Shaded Regions
ax2.axvspan(0, 145, color="green", alpha=0.2)
ax2.axvspan(1345, 1500, color="green", alpha=0.2)
ax2.axvspan(145, 1345, color="blue", alpha=0.2)

ax2.set_title("Flight Profile", fontsize=12, fontweight="bold")

legend_elements = [
    Patch(facecolor="blue", edgecolor="blue", alpha=0.2, label="BADA"),
    Patch(facecolor="green", edgecolor="green", alpha=0.2, label="EDB"),
]
ax2.legend(handles=legend_elements, loc="lower left")

# ZOOM CONNECTION ###############################

# Connect the LAST reference point (largest weight) to the right plot
last_x = 315
last_y = 19.5
bbox = ax2.get_position()

# Connection to Top-Left of ax2
con_top = ConnectionPatch(
    xyA=(last_x, last_y),
    coordsA=ax1.transData,
    xyB=(bbox.x0, bbox.y1),
    coordsB="figure fraction",
    color="black",
    linestyle=":",
    linewidth=1,
)
fig.add_artist(con_top)

# Connection to Bottom-Left of ax2
con_bottom = ConnectionPatch(
    xyA=(last_x, last_y),
    coordsA=ax1.transData,
    xyB=(bbox.x0, bbox.y0),
    coordsB="figure fraction",
    color="black",
    linestyle=":",
    linewidth=1,
)
fig.add_artist(con_bottom)

# EXPORT ########################################

try:
    figure_name = str(Path(__file__).stem + ".svg")
except NameError:
    figure_name = "plot_output.svg"

plt.savefig(fname=figure_name, format="svg", bbox_inches="tight", transparent=False)

plt.show()
