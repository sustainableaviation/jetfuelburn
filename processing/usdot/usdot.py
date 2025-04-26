# %%
import pint
ureg = pint.get_application_registry()
import pandas as pd
import pint_pandas


def process_data_usdot_t2(
    path_csv_t2: str = 'jetfuelburn/data/USDOT/T_SCHEDULE_T2.csv',
    path_csv_aircraft_types: str = 'jetfuelburn/data/USDOT/T_SCHEDULE_T2_WITH_ICAO.csv',
) -> pd.DataFrame:
    """
    Function for processing the US DOT T2 dataset.

    Notes
    -----
    Required data must be downloaded from the US Department of Transport:
    - ["AircraftType": `L_AIRCRAFT_TYPE.csv`]()
    - ["Data Tools: Download": `T_SCHEDULE_T2.csv`]()

    See Also
    --------
    Additional information can be found at:
    - [US DOT: BTS: Air Carrier Summary Data (Form 41 and 298C Summary Data)](https://www.transtats.bts.gov/Tables.asp?QO_VQ=EGD&QO)
    - [US DOT: BTS: Air Carrier Summary Data: T2 (U.S. Air Carrier Traffic And Capacity Statistics by Aircraft Type)](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FIH)
    """

    df_t2 = pd.read_csv(
        filepath_or_buffer=path_csv_t2,
        header=0,
        index_col=None,
        sep=',',
    )
    df_aircraft_types = pd.read_csv(
        filepath_or_buffer=path_csv_aircraft_types,
        header=0,
        index_col=None,
        sep=',',
        names=['AIRCRAFT_TYPE', 'Aircraft Designation (US DOT Schedule T2)'],
    )
    df_t2 = pd.merge(
        left=df_t2,
        right=df_aircraft_types,
        on='AIRCRAFT_TYPE',
        how='left',
    )

    """
    Column names in the T2 dataset sometimes have numbers appended.
    In order to unify the column names, these numbers are removed.

    For example, as of 11-2024, the dictionary generated below will look like:

    dict_columns_for_renaming = {
        'AVL_SEAT_MILES_320': 'AVL_SEAT_MILES',
        'REV_PAX_MILES_140': 'REV_PAX_MILES',
        'REV_TON_MILES_240': 'REV_TON_MILES',
        'AVL_TON_MILES_280': 'AVL_TON_MILES',
        'AIRCRAFT_FUELS_921': 'AIRCRAFT_FUELS',
        'CARRIER_GROUP': 'CARRIER_GROUP',
        'AIRCRAFT_CONFIG': 'AIRCRAFT_CONFIG',
        'AIRCRAFT_TYPE': 'AIRCRAFT_TYPE',
    }
    """

    dict_columns_and_units = {
        'AVL_SEAT_MILES': 'pint[miles]',
        'REV_PAX_MILES': 'pint[miles]',
        'REV_TON_MILES': 'pint[miles*short_ton]',
        'AVL_TON_MILES': 'pint[miles*short_ton]',
        'AIRCRAFT_FUELS': 'pint[gallons]',
        'CARRIER_GROUP': 'pint[]',
        'AIRCRAFT_CONFIG': 'pint[]',
        'AIRCRAFT_TYPE': 'pint[]',
    }
    dict_columns_for_renaming = {df_t2.filter(like=column_name).columns[0]: column_name for column_name in dict_columns_and_units.keys()}
    df_t2 = df_t2.rename(columns=dict_columns_for_renaming)
    df_t2 = df_t2.astype(dict_columns_and_units)

    df_t2['AIRCRAFT_FUELS'] = df_t2['AIRCRAFT_FUELS'].pint.to(ureg('liters'))
    df_t2['AVL_SEAT_MILES'] = df_t2['AVL_SEAT_MILES'].pint.to(ureg('km'))
    df_t2['REV_PAX_MILES'] = df_t2['REV_PAX_MILES'].pint.to(ureg('km'))
    df_t2['REV_TON_MILES'] = df_t2['REV_TON_MILES'].pint.to(ureg('km*kg'))
    df_t2['AVL_TON_MILES'] = df_t2['AVL_TON_MILES'].pint.to(ureg('km*kg'))
    
    # DATA FILTERING
    
    df_t2 = df_t2.loc[df_t2['CARRIER_GROUP'] == 3] # major carriers only
    df_t2 = df_t2.drop(columns=['CARRIER_GROUP', 'AIRCRAFT_CONFIG'])

    list_numeric_columns = [
        'AVL_SEAT_MILES',
        'REV_PAX_MILES',
        'REV_TON_MILES',
        'AVL_TON_MILES',
        'AIRCRAFT_FUELS',
    ]
    df_t2[list_numeric_columns] = df_t2[list_numeric_columns].replace(
        to_replace=0,
        value=pd.NA
    )

    # CUSTOM COLUMN CALCULATIONS

    df_t2['Fuel/Available Seat Distance'] = df_t2['AIRCRAFT_FUELS']/df_t2['AVL_SEAT_MILES']
    df_t2['Fuel/Revenue Seat Distance'] = df_t2['AIRCRAFT_FUELS']/df_t2['REV_PAX_MILES']
    df_t2['Fuel/Available Weight Distance'] = df_t2['AIRCRAFT_FUELS']/df_t2['AVL_TON_MILES']
    df_t2['Fuel/Revenue Weight Distance'] = df_t2['AIRCRAFT_FUELS']/df_t2['REV_TON_MILES']

    # SANITY CHECKS

    df_t2 = df_t2.loc[df_t2['REV_PAX_MILES'] <= df_t2['AVL_SEAT_MILES']]

    # COLUMN SELECTION

    list_return_columns = [
        'Aircraft Designation (US DOT Schedule T2)',
        'Fuel/Available Seat Distance',
        'Fuel/Revenue Seat Distance',
        'Fuel/Available Weight Distance',
        'Fuel/Revenue Weight Distance',
    ]
    df_t2 = df_t2[list_return_columns]

    # AIRCRAFT AVERGAGES

    agg_dict = {
        'Fuel/Available Seat Distance': 'mean',
        'Fuel/Revenue Seat Distance': 'mean',
        'Fuel/Available Weight Distance': 'mean',
        'Fuel/Revenue Weight Distance': 'mean',
    }
    df_t2 = df_t2.groupby(
        by='Aircraft Designation (US DOT Schedule T2)',
        as_index=False,
    ).agg(agg_dict)

    # UNIT CONVERSION

    density_jetfuel = ((775+840)/2) * ureg('g/liter') # https://en.wikipedia.org/wiki/Jet_fuel
    density_jetfuel = density_jetfuel.to('kg/liter')
    df_t2['Fuel/Available Seat Distance'] = df_t2['Fuel/Available Seat Distance'] * density_jetfuel
    df_t2['Fuel/Revenue Seat Distance'] = df_t2['Fuel/Revenue Seat Distance'] * density_jetfuel
    df_t2['Fuel/Available Weight Distance'] = df_t2['Fuel/Available Weight Distance'] * density_jetfuel
    df_t2['Fuel/Revenue Weight Distance'] = df_t2['Fuel/Revenue Weight Distance'] * density_jetfuel
    df_t2 = df_t2.set_index('Aircraft Designation (US DOT Schedule T2)')

    return df_t2

df = process_data_usdot_t2(
    path_csv_aircraft_types='data/L_AIRCRAFT_TYPE.csv',
    path_csv_t2='data/T_SCHEDULE_T2.csv'
)