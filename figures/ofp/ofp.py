# %%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# sys
import os
from pathlib import Path

# plotting
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# unit conversion
cm = 1 / 2.54  # for inches-cm conversion

# data science
import numpy as np
import pandas as pd

# SETUP #########################################

plt.rcParams.update({"font.family": "Arial", "font.size": 12})

# DATA IMPORT ###################################

# (Placeholder for data if needed in future)

# DATA MANIPULATION #############################

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num="ofp",
    nrows=1,
    ncols=1,
    dpi=300,
    figsize=(20 * cm, 10 * cm),  # A4=(210x297)mm,
)

# AXIS LIMITS ################

y_max = 35000
x_max = 1000

ax.set_xlim(-50, x_max)
ax.set_ylim(0, y_max)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis="both", which="both", labelbottom=False, labelleft=False)

# GRIDS ######################

ax.grid(which="major", axis="both", linestyle="-", linewidth=0.5)
ax.grid(which="minor", axis="both", linestyle=":", linewidth=0.5)

# AXIS LABELS ################

ax.set_xlabel("Distance or Time")
ax.set_ylabel("Altitude")
ax.yaxis.set_label_coords(-0.02, 0.5)

# PLOTTING ###################

# Lower third background: light orange
ax.axhspan(0, y_max / 3, facecolor='moccasin', alpha=0.6, label="Climb Regime 1")

# Upper two thirds background: light red
ax.axhspan(y_max / 3, y_max, facecolor='mistyrose', alpha=0.6, label="Climb Regime 2")

# TRAJECTORY ARROWS ##########

border_y = y_max / 3
mid_x = 205
wp2_upper = (800, 30000)

# Orange arrow: Up to the border
ax.annotate(
    "",
    xy=(mid_x, border_y),
    xytext=(0, 0),
    arrowprops=dict(arrowstyle="->", color="orange", lw=2),
)

# Red arrow: From the border to the upper WP2
ax.annotate(
    "",
    xy=wp2_upper,
    xytext=(mid_x, border_y),
    arrowprops=dict(arrowstyle="->", color="red", lw=2),
)

# STEEPER TRAJECTORY (BLACK) ####

# First steeper segment (from 0,0)
mid_x_steep = 150 # Reaches border earlier than mid_x (205)
ax.annotate(
    "",
    xy=(mid_x_steep, border_y),
    xytext=(0, 0),
    arrowprops=dict(arrowstyle="->", color="black", lw=2, linestyle='--'),
)

# Second steeper segment (to 30000 alt)
# Reaches 30000 alt at x=600 (before WP2 x=800)
target_x_steep = 600
ax.annotate(
    "",
    xy=(target_x_steep, 30000),
    xytext=(mid_x_steep, border_y),
    arrowprops=dict(arrowstyle="->", color="black", lw=2, linestyle='--'),
)
# Single Level-Off label for the steeper profile
ax.text((mid_x_steep + target_x_steep)/2 + 200, (border_y + 30000)/2 + 5500, "Level-Off", color="black", fontsize=11, ha="right", va="bottom", rotation=29)

# Level off segment for steeper profile
ax.plot([target_x_steep, 800], [30000, 30000], color='black', linestyle='--', linewidth=2, zorder=6)

# ANGLE ANNOTATIONS (ROC) ####

import numpy as np

def draw_arc_as_points(ax, center, rx, ry, theta1, theta2, **kwargs):
    """Draws an arc by plotting points, more reliable for SVG export than Patches.Arc."""
    t = np.linspace(np.radians(theta1), np.radians(theta2), 100)
    x = center[0] + rx * np.cos(t)
    y = center[1] + ry * np.sin(t)
    ax.plot(x, y, **kwargs)

def get_visual_slope_angle(dx, dy, ax, fig):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    width, height = fig.get_size_inches()
    dx_norm = dx / (xlim[1] - xlim[0]) * width
    dy_norm = dy / (ylim[1] - ylim[0]) * height
    return np.degrees(np.arctan2(dy_norm, dx_norm))

# Setup dimensions
rx = 180 # increased radius slightly for better label clearance
xlim = ax.get_xlim()
ylim = ax.get_ylim()
width, height = fig.get_size_inches()
ry = rx * (width / height) * ((ylim[1] - ylim[0]) / (xlim[1] - xlim[0]))

angle1 = get_visual_slope_angle(mid_x, border_y, ax, fig)
angle2 = get_visual_slope_angle(800 - mid_x, 30000 - border_y, ax, fig)

# Draw Horizontal Reference Lines
ax.hlines(y=0, xmin=0, xmax=rx, color="black", linestyle="--", linewidth=1, alpha=0.3, zorder=10)
ax.hlines(y=border_y, xmin=mid_x, xmax=mid_x + rx, color="black", linestyle="--", linewidth=1, alpha=0.3, zorder=10)

# Draw the Arcs (matching arrow colors)
draw_arc_as_points(ax, (0, 0), rx, ry, 0, angle1, color="orange", lw=2.5, zorder=12)
draw_arc_as_points(ax, (mid_x, border_y), rx, ry, 0, angle2, color="red", lw=2.5, zorder=12)

# ROC labels moved inside the arcs
# We position them at roughly midpoint of the arc angle
label_r_x = rx * 0.7  # Moved inside
label_r_y = ry * 0.7  # Moved inside

t1 = np.radians(angle1 / 2)
ax.text(label_r_x * np.cos(t1), label_r_y * np.sin(t1), "ROC1", color="orange", fontweight="bold", ha="center", va="center", zorder=11, fontsize=11)

t2 = np.radians(angle2 / 2)
ax.text(mid_x + label_r_x * np.cos(t2), border_y + label_r_y * np.sin(t2) - 500, "ROC2", color="red", fontweight="bold", ha="center", va="center", zorder=11, fontsize=11)

# WAYPOINTS ##################

# Grey dashed line between WP2 points (Thicker)
ax.plot([800, 800], [0, 30000], color='grey', linestyle='--', linewidth=2.5, alpha=0.6, zorder=5)

waypoints = [
    (0, 0, "WP1"),
    (800, 0, "WP2"),
    (800, 30000, "WP2")
]

for x, y, label in waypoints:
    ax.plot(x, y, marker='o', color='black', markersize=4)
    # Move WP1 and lower WP2 below the axis, others above
    y_offset = -15 if (label == "WP1" or (label == "WP2" and y == 0)) else 5
    ax.annotate(
        label, 
        (x, y), 
        textcoords="offset points", 
        xytext=(0, y_offset), 
        ha='center', 
        fontsize=11,
        fontweight='bold'
    )

# LEGEND ####################

ax.legend(
    loc="upper left",
    ncol=1,
    fontsize=11,
    frameon=True,
    framealpha=0.8
)

# EXPORT #########################################

figure_name: str = str(Path(__file__).parent / (Path(__file__).stem + ".svg"))

plt.savefig(fname=figure_name, format="svg", bbox_inches="tight", transparent=False)

print(f"Figure saved to {figure_name}")
