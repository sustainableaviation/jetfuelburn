# %%
import pandas as pd
import numpy as np


def get_all_distances(sheets):
    """
    Determine the complete set of distance headers across all sheets.

    Parameters:
    sheets (dict): Dictionary of DataFrames from pd.read_excel(sheet_name=None).

    Returns:
    list: Sorted list of unique distances (e.g., [125, 250, ..., 6500]).
    """
    all_distances = set()
    for df in sheets.values():
        label_location = (
            df[df == "Standard flight distances (nm) [1nm = 1.852 km]"].stack().index[0]
        )
        label_row, label_col = label_location
        distances = (
            df.iloc[label_row + 1, label_col:]
            .dropna()
            .astype(float)
            .astype(int)
            .tolist()
        )
        all_distances.update(distances)
    return sorted(all_distances)


def extract_fuel_data(file_path):
    """
    Extract fuel consumption data from an Excel file with standardized distance headers.

    Parameters:
    file_path (str): Path to the Excel file.

    Returns:
    dict: Structure {aircraft_type: {subcategory: {distance: fuel_value}}}.
          Distances are standardized across all sheets, with NaN for missing values.
    """
    # Read all sheets from the Excel file without headers
    sheets = pd.read_excel(file_path, sheet_name=None, header=None)

    # Get the standardized set of distances from all sheets
    standard_distances = get_all_distances(sheets)

    # Initialize the result dictionary
    fuel_data = {}

    for sheet_name, df in sheets.items():
        # Find the location of the distance label
        label_location = (
            df[df == "Standard flight distances (nm) [1nm = 1.852 km]"].stack().index[0]
        )
        label_row, label_col = label_location

        # Extract sheet-specific distances
        sheet_distances = (
            df.iloc[label_row + 1, label_col:]
            .dropna()
            .astype(float)
            .astype(int)
            .tolist()
        )

        # Find the start of the fuel section
        fuel_row = df[df.iloc[:, 0] == "Fuel (kg)"].index[0]

        # Find the end of the fuel section
        end_row_candidates = df.iloc[fuel_row + 1 :].index[
            df.iloc[fuel_row + 1 :, 0].notna()
        ]
        end_row = end_row_candidates[0] if len(end_row_candidates) > 0 else df.shape[0]

        # Initialize dictionary for this aircraft
        aircraft_fuel_dict = {}

        # Process each row in the fuel section
        for idx in range(fuel_row + 1, end_row):
            subcategory = str(df.iloc[idx, 1]).strip()  # e.g., "Take off"
            # Extract fuel values aligned with sheet-specific distances
            fuel_values = df.iloc[
                idx, label_col : label_col + len(sheet_distances)
            ].values

            # Map sheet-specific distances to fuel values
            sheet_dict = {dist: val for dist, val in zip(sheet_distances, fuel_values)}

            # Create standardized dictionary with all distances
            subcategory_dict = {
                dist: (
                    sheet_dict[dist]
                    if dist in sheet_dict and pd.notna(sheet_dict[dist])
                    else np.nan
                )
                for dist in standard_distances
            }

            aircraft_fuel_dict[subcategory] = subcategory_dict

        # Store this aircraft's data
        fuel_data[sheet_name] = aircraft_fuel_dict

    return fuel_data


# Example usage:
# fuel_info = extract_fuel_data("path/to/your/excel_file.xls")
# print(fuel_info)
# %%

import numpy as np
import pandas as pd


def clean_nan_entries(data):
    """
    Remove all NaN-related entries from a nested dictionary of aircraft fuel data for multiple aircraft.

    Parameters:
    data (dict): Nested dictionary with structure {aircraft: {subcategory: {distance: fuel_value}}}.

    Returns:
    dict: Cleaned dictionary with no NaN keys, values, or invalid subcategories for all aircraft.
    """
    cleaned_data = {}

    for aircraft, subcategories in data.items():
        cleaned_subcategories = {}

        for subcategory, distance_dict in subcategories.items():
            # Skip subcategories that are 'nan' or NaN
            if subcategory == "nan" or pd.isna(subcategory):
                continue

            cleaned_distances = {}
            for distance, fuel in distance_dict.items():
                # Check if distance is not NaN and fuel is not NaN
                if not (
                    isinstance(distance, (float, np.floating)) and pd.isna(distance)
                ) and not pd.isna(fuel):
                    # Convert distance to int if numeric, otherwise keep as is
                    cleaned_key = (
                        int(distance)
                        if isinstance(distance, (int, float, np.floating))
                        else distance
                    )
                    cleaned_distances[cleaned_key] = float(
                        fuel
                    )  # Ensure fuel is a float

            # Only add subcategory if it has valid entries
            if cleaned_distances:
                cleaned_subcategories[subcategory] = cleaned_distances

        # Only add aircraft if it has valid subcategories
        if cleaned_subcategories:
            cleaned_data[aircraft] = cleaned_subcategories

    return cleaned_data


# %%
