from jetfuelburn import ureg
from jetfuelburn.reducedorder import (
    sacchi_etal,
    yanto_etal,
    montlaur_etal,
    seymour_etal,
    aim2015,
    eea_emission_inventory_2009,
    myclimate,
)
from jetfuelburn.statistics import usdot
import pandas as pd
import matplotlib.pyplot as plt

distances_km = range(1000, 7001, 100)

D_CLIMB = 300 * ureg.km
D_DESCENT = 200 * ureg.km
YEAR = 2024

# Average pax counts from US DOT data
PAX_A320 = 128  # A320 average passengers
PAX_B738 = 126  # 737-800 average passengers
PAX_B772 = 228  # B772 average passengers (kept as before)

# Typical max seat configurations
PAX_MAX_A320 = 180
PAX_MAX_B738 = 189
PAX_MAX_B772 = 365

KG_PER_PAX = 100  # kg per pax incl. luggage

# Aircraft / parameter configurations per model.
# sacchi_etal and montlaur_etal have no aircraft designator — seat count is varied instead.
# myclimate: A320/B737 are short-haul only (≤2500 km); A330/B777 are long-haul only (≥1500 km).
CONFIGS = {
    "sacchi_etal": [
        {
            "label": f"A320 (pax_max={PAX_MAX_A320}, pax={PAX_A320})",
            "pax_max": PAX_MAX_A320,
            "pax": PAX_A320,
        },
        {
            "label": f"B738 (pax_max={PAX_MAX_B738}, pax={PAX_B738})",
            "pax_max": PAX_MAX_B738,
            "pax": PAX_B738,
        },
        {
            "label": f"B772 (pax_max={PAX_MAX_B772}, pax={PAX_B772})",
            "pax_max": PAX_MAX_B772,
            "pax": PAX_B772,
        },
    ],
    "yanto_etal": [
        {
            "label": f"A320 ({PAX_A320} pax)",
            "acft": "A320",
            "PL": PAX_A320 * KG_PER_PAX * ureg.kg,
        },
        {
            "label": f"B738 ({PAX_B738} pax)",
            "acft": "B738",
            "PL": PAX_B738 * KG_PER_PAX * ureg.kg,
        },
        {
            "label": f"B772 ({PAX_B772} pax)",
            "acft": "B772",
            "PL": PAX_B772 * KG_PER_PAX * ureg.kg,
        },
    ],
    "montlaur_etal": [
        {"label": "180 seats", "available_seats": 180},
        {"label": "250 seats", "available_seats": 260},
        {"label": "365 seats", "available_seats": 365},
    ],
    "seymour_etal": [
        {"label": "A320", "acft": "A320"},
        {"label": "B738", "acft": "B738"},
        {"label": "B772", "acft": "B772"},
    ],
    "aim2015": [
        {
            "label": "size class 3 (regional)",
            "acft_size_class": 3,
            "PL": 100 * KG_PER_PAX * ureg.kg,
        },
        {
            "label": f"size class 5 (narrow-body, A320 {PAX_A320} pax)",
            "acft_size_class": 5,
            "PL": PAX_A320 * KG_PER_PAX * ureg.kg,
        },
        {
            "label": f"size class 7 (wide-body, B772 {PAX_B772} pax)",
            "acft_size_class": 7,
            "PL": PAX_B772 * KG_PER_PAX * ureg.kg,
        },
    ],
    "eea_emission_inventory_2009": [
        {"label": "A320", "acft": "A320"},
        {"label": "B763", "acft": "B763"},
        {"label": "B777", "acft": "B777"},
    ],
    "myclimate": [
        {"label": "standard aircraft", "acft": "standard aircraft"},
        {"label": "A320 (≤2500 km)", "acft": "A320"},
        {"label": "B777 (≥1500 km)", "acft": "B777"},
    ],
    "usdot": [
        {
            "label": f"A320-100/200 ({PAX_A320} pax)",
            "acft": "Airbus Industrie A320-100/200",
            "pax": PAX_A320,
            "year": 2024,
        },
        {
            "label": f"B737-800 ({PAX_B738} pax)",
            "acft": "Boeing 737-800",
            "pax": PAX_B738,
            "year": 2024,
        },
        {
            "label": f"B777-200ER ({PAX_B772} pax)",
            "acft": "Boeing 777-200ER/200LR/233LR",
            "pax": PAX_B772,
            "year": 2024,
        },
    ],
}


def _run_model(model_name, cfg, R):
    """Return total fuel in kg for one model/config/distance, or NaN on failure."""
    try:
        if model_name == "sacchi_etal":
            return (
                sacchi_etal.calculate_fuel_consumption(
                    year=YEAR, pax_max=cfg["pax_max"], pax=cfg["pax"], R=R
                )
                .to("kg")
                .magnitude
            )

        if model_name == "yanto_etal":
            return (
                yanto_etal.calculate_fuel_consumption(
                    acft=cfg["acft"], R=R, PL=cfg["PL"]
                )
                .to("kg")
                .magnitude
            )

        if model_name == "montlaur_etal":
            fuel_per_km = montlaur_etal.calculate_fuel_consumption(
                distance=R, available_seats=cfg["available_seats"]
            )
            return (fuel_per_km * R * cfg["available_seats"]).to("kg").magnitude

        if model_name == "seymour_etal":
            return (
                seymour_etal.calculate_fuel_consumption(acft=cfg["acft"], R=R)
                .to("kg")
                .magnitude
            )

        if model_name == "aim2015":
            res = aim2015.calculate_fuel_consumption(
                acft_size_class=cfg["acft_size_class"],
                D_climb=D_CLIMB,
                D_cruise=R - D_CLIMB - D_DESCENT,
                D_descent=D_DESCENT,
                PL=cfg["PL"],
            )
            return sum(v.to("kg").magnitude for v in res.values())

        if model_name == "eea_emission_inventory_2009":
            res = eea_emission_inventory_2009.calculate_fuel_consumption(
                acft=cfg["acft"], R=R
            )
            return res["mass_fuel_total"].to("kg").magnitude

        if model_name == "myclimate":
            return (
                myclimate.calculate_fuel_consumption(acft=cfg["acft"], x=R)
                .to("kg")
                .magnitude
            )

        if model_name == "usdot":
            fuel_per_pax = usdot.calculate_fuel_consumption_per_seat(
                year=cfg["year"], acft=cfg["acft"], R=R
            )
            return (fuel_per_pax * cfg["pax"]).to("kg").magnitude

    except Exception:
        return float("nan")


# Build one DataFrame per model: index = distance_km, columns = config labels
results = {}
for model_name, configs in CONFIGS.items():
    data = {}
    for cfg in configs:
        data[cfg["label"]] = [
            _run_model(model_name, cfg, d * ureg.km) for d in distances_km
        ]
    results[model_name] = pd.DataFrame(data, index=list(distances_km))
    results[model_name].index.name = "distance_km"

# Print summary
for model_name, df in results.items():
    print(f"\n=== {model_name} ===")
    print(df.to_string())

# Save all results to a single CSV with a model column
combined = pd.concat({name: df for name, df in results.items()}, axis=1)
combined.to_csv("distance_sweep_results.csv")

# Plot: one subplot per model, one line per config
fig, axes = plt.subplots(
    nrows=len(CONFIGS),
    ncols=1,
    figsize=(9, 4 * len(CONFIGS)),
    sharex=True,
)

SHORT_HAUL_LIMIT_KM = 5000
SHORT_HAUL_AIRCRAFT = {"A320", "B738", "B737-800"}

usdot_df = results["usdot"]

for ax, (model_name, df) in zip(axes, results.items()):
    for col in df.columns:
        is_short_haul = any(a in col for a in SHORT_HAUL_AIRCRAFT)
        series = df[col][df.index <= SHORT_HAUL_LIMIT_KM] if is_short_haul else df[col]
        ax.plot(series.index, series, label=col)

    if model_name != "usdot":
        for col in usdot_df.columns:
            is_short_haul = any(a in col for a in SHORT_HAUL_AIRCRAFT)
            series = (
                usdot_df[col][usdot_df.index <= SHORT_HAUL_LIMIT_KM]
                if is_short_haul
                else usdot_df[col]
            )
            ax.plot(
                series.index,
                series,
                linestyle="--",
                linewidth=1,
                alpha=0.6,
                label=f"DOT: {col}",
            )

    ax.set_title(model_name)
    ax.set_ylabel("Fuel burn (kg)")
    ax.set_xlabel("Distance (km)")
    ax.tick_params(labelbottom=True)
    ax.legend(fontsize=7)
    ax.grid(True)
plt.tight_layout()
plt.savefig("distance_sweep_plots.png", dpi=150)
plt.show()
