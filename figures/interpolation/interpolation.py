# %%
# runs code as interactive cell
# https://code.visualstudio.com/docs/python/jupyter-support-py

# IMPORTS #######################################

# sys
import os
import bisect

# plotting
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# unit conversion
cm = 1 / 2.54  # for inches-cm conversion
# data science
import numpy as np

# SETUP #########################################

plt.rcParams.update({"font.family": "Arial", "font.size": 12})

# DATA IMPORT ###################################


def _interpolate(
    x_val: float | int, x_list: list[float | int], y_list: list[float | int]
):
    """
    Finds y_val for a given x_val using linear interpolation.
    """
    # Boundary checks removed for visualization purposes

    i = bisect.bisect_right(x_list, x_val)
    x0, x1 = x_list[i - 1], x_list[i]
    y0, y1 = y_list[i - 1], y_list[i]

    k = (y1 - y0) / (x1 - x0)
    y_val = y0 + k * (x_val - x0)

    return y_val, x0, x1, y0, y1, k


# DATA MANIPULATION #############################

# 1. Define known data points (The "List")
x_known = [0, 10, 20, 30]
y_known = [10, 50, 90, 60]

# 2. Define target value to interpolate
x_target = 16

# 3. Calculate interpolation
y_target, x0, x1, y0, y1, k = _interpolate(x_target, x_known, y_known)

# FIGURE ########################################

# SETUP ######################

fig, ax = plt.subplots(
    num="main",
    nrows=1,
    ncols=1,
    dpi=300,
    figsize=(20 * cm, 10 * cm),
)

# AXIS LIMITS ################

ax.set_xlim(0, 32)
ax.set_ylim(0, 110)

# TICKS AND LABELS ###########

ax.minorticks_on()
ax.tick_params(axis="x", which="minor", bottom=True)

# Manually set ticks to match our data points
x_ticks = x_known
ax.set_xticks(x_ticks + [x_target])
ax.set_xticklabels([str(x) for x in x_ticks] + [r"$x_{val}$"])

y_ticks = [0, 20, 40, 60, 80, 100]
ax.set_yticks(y_ticks)

# GRIDS ######################

ax.grid(which="major", axis="y", linestyle="-", linewidth=0.5, alpha=0.5)
ax.grid(which="minor", axis="y", linestyle=":", linewidth=0.5, alpha=0.5)
ax.grid(which="major", axis="x", linestyle="-", linewidth=0.5, alpha=0.5)

# AXIS LABELS ################

ax.set_xlabel("Input (x)")
ax.set_ylabel("Output (y)")

# PLOTTING ###################

# 1. Plot the "Known" function (Piecewise Linear)
plt.plot(
    x_known,
    y_known,
    color="black",
    linestyle="-",
    linewidth=1.5,
    marker="o",
    markersize=6,
    label="Known Data",
    zorder=2,
)

# 2. Plot the interpolated point
plt.scatter(
    [x_target],
    [y_target],
    color="tab:red",
    marker="*",
    s=200,
    label="Interpolated Point",
    zorder=10,
)

# 3. Drop lines for the target point
# Vertical line to X axis
plt.plot(
    [x_target, x_target], [0, y_target], color="tab:red", linestyle="--", linewidth=1
)

# Horizontal line to Y axis
# (From x=0 to x=target)
plt.plot(
    [0, x_target], [y_target, y_target], color="tab:red", linestyle="--", linewidth=1
)


# ANNOTATIONS ###################

# Label y_val on the Y-axis
ax.annotate(
    r"$y_{val}$",
    xy=(0, y_target),  # Point on the Y-axis
    xytext=(-10, 0),  # 10 points to the left
    textcoords="offset points",  # Relative positioning
    ha="right",
    va="center",
    color="tab:red",
    fontsize=12,
    fontweight="bold",
)

# Annotate x0, x1 points
ax.annotate(
    r"$(x_{i-1}, y_{i-1})$",
    xy=(x0, y0),
    xytext=(x0 - 6, y0 + 5),
    fontsize=12,
    arrowprops=dict(arrowstyle="->", color="black", lw=0.5),
)

ax.annotate(
    r"$(x_{i}, y_{i})$",
    xy=(x1, y1),
    xytext=(x1 + 2, y1 + 5),
    fontsize=12,
    arrowprops=dict(arrowstyle="->", color="black", lw=0.5),
)

# Visualizing the Triangle (Rise and Run)
plt.plot([x0, x1], [y0, y0], color="gray", linestyle=":", linewidth=1)
plt.plot([x1, x1], [y0, y1], color="gray", linestyle=":", linewidth=1)

# Annotate Slope (k)
ax.text(
    x0 + (x1 - x0) / 2, y0 - 5, r"$\Delta x$", ha="center", fontsize=12, color="gray"
)
ax.text(
    x1 + 0.5,
    y0 + (y1 - y0) / 2,
    r"$\Delta y$",
    ha="left",
    va="center",
    fontsize=12,
    color="gray",
)

# LEGEND ####################

ax.legend(
    loc="lower right", frameon=True, fancybox=True, framealpha=1, edgecolor="lightgray"
)

# EXPORT #########################################

from pathlib import Path

try:
    filename = Path(__file__).stem + ".svg"
except NameError:
    filename = "linear_interpolation.svg"

plt.savefig(fname=filename, format="svg", bbox_inches="tight", transparent=False)
plt.show()
