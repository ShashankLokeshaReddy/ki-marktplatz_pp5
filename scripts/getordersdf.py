"""Functions to read order data from different sources to return as dataframe.
"""
# Third party libraries
import datetime
import os
import pathlib
from enum import Enum
import numpy as np
import pandas as pd


# Current script directory
script_directory = pathlib.Path(__file__).parent.resolve()
# Default path of the order database excel file
default_westaflex_table_path = os.path.join(script_directory, '..', 'data',
                                            "20220706_Auftragsdatenbank_last_10_modified.xlsm")

# The returned dataframes need to have the following column names, more are ok
common_dataframe = pd.DataFrame(columns=['job',
                                         'order_release',
                                         'status',
                                         'machines',
                                         'selected_machine',
                                         'tool',
                                         'setuptime',
                                         'shift',
                                         'duration_machine',
                                         'duration_manual',
                                         'deadline',
                                         'latest_start',
                                         'calculated_start',
                                         'calculated_end',
                                         'planned_start',
                                         'planned_end',
                                         'final_start',
                                         'final_end'])


class JobStatus(Enum):
    UNKNOWN = 1
    UNPLANNED = 2
    CALCULATED = 3
    PLANNED = 4
    IN_PROGRESS = 5


def get_date(datetime_object):
    """Extracts the date from a datetime object as a string.

    Args:
        datetime_object (_type_): The datetime object that contains the date

    Returns:
        _type_: A string, which contains the date
    """
    return str(datetime_object)[:11]


def combine_datetime_columns(df, col_name):
    """Combines two columns into one datetime column, where one column contains the date and one column contains the time.
    The date column is assumed to be in the col_name column and time is in the directly following column.
    The result will be stored in the col_name column.

    Args:
        df (_type_): A pandas dataframe containing the orders
        col_name (_type_): the selected column for datetime combination

    Returns:
        _type_: a pandas dataframe containing the orders with a combined datetime column
    """
    df[col_name] = df[col_name].apply(get_date) + df.iloc[
        :, df.columns.get_loc(col_name) + 1
    ].astype(str)
    df[col_name] = pd.to_datetime(df[col_name], errors='ignore')
    return df


def set_order_status(order_df):
    """Assign a job status to each order according to their time stamps.

    Args:
        order_df (_type_): pandas dataframe containing the orders

    Returns:
        _type_: pandas dataframe with an additional status column
    """
    order_df["status"] = JobStatus.UNKNOWN
    for idx in order_df.index:
        if pd.notnull(order_df.loc[idx, "latest_start"]) and pd.notnull(
            order_df.loc[idx, "deadline"]
        ):
            order_df.loc[idx, "status"] = JobStatus.UNPLANNED
        if pd.notnull(order_df.loc[idx, "calculated_start"]) and pd.notnull(
            order_df.loc[idx, "calculated_end"]
        ):
            order_df.loc[idx, "status"] = JobStatus.CALCULATED
        if pd.isnull(order_df.loc[idx, "planned_start"]) and pd.notnull(
            order_df.loc[idx, "planned_end"]
        ):
            order_df.loc[idx, "status"] = JobStatus.PLANNED
        if pd.notnull(order_df.loc[idx, "final_start"]):
            order_df.loc[idx, "status"] = JobStatus.IN_PROGRESS
    # TODO compute final_end for orders in_work, where this is not given (order is finished in future)
    return order_df


def filter_orders(order_df, planning_period_start, planning_period_end):
    """Removes orders, which are marked for removal and are scheduled outside of the planning period.
    Orders are outside of the planning period if they are already finished (final_end before planning_period_start)
    or if they are planned after the planning period (planning_start after planning_period_end)

    Args:
        order_def (_type_): pandas dataframe containing the orders
        planning_period_start (_type_): start of planning period in datetime
        planning_period_end (_type_): end of planning period in datetime

    Returns:
        _type_: pandas dataframe of filtered orders
    """
    order_df = order_df[
        (pd.isnull(order_df["final_end"]))
        | (order_df["final_end"] > planning_period_start)
    ]
    order_df = order_df[
        (pd.isnull(order_df["planned_start"]))
        | (order_df["planned_start"] < planning_period_end)
    ]
    return order_df


def get_westaflex_orders(path: str = default_westaflex_table_path) -> pd.DataFrame:
    """
    Opens an excel document to return its listed orders as a pandas dataframe.

    Requires the excel document to have following specific structure:
        A sheet named 'Datenbank_Auftragsdaten'.
        The orders starting at row 15.
        Column titles like 'Artikelnummer' and more.

    Parameters
    ----------
    path : str
        Path to the excel order database.

    Returns
    -------
    DataFrame
        Table of orders as pandas dataframe. Column names:
            job, item, order_release, machine, selected_machine, tool,
            setuptime, duration_machine,
            duration_manual, deadline, calculated_start, calculated_end,
            planned_start, planned_end, final_start, final_end
    """
    sheet_name = 'Datenbank_Auftragsdaten'
    order_df = pd.read_excel(path, sheet_name)  # Read file
    order_df = order_df.rename(columns=order_df.iloc[10])
    # Combine separate date time columns to datetime
    order_df = combine_datetime_columns(
        order_df, "Spätester Bearbeitungsbeginn")
    order_df = combine_datetime_columns(
        order_df, "spätester Fertigstellungszeitpunkt")
    order_df = combine_datetime_columns(
        order_df, "Berechneter Bearbei-tungsbeginn")
    order_df = combine_datetime_columns(
        order_df, "Berechneter Fertigstellungs-zeitpunkt")
    order_df = combine_datetime_columns(order_df, "PLAN-Bearbeitungs-beginn")
    order_df = combine_datetime_columns(
        order_df, "PLAN-Fertigstellungs-zeitpunkt")
    order_df = combine_datetime_columns(order_df, "IST- Bearbeitungs-beginn")
    order_df = combine_datetime_columns(
        order_df, "IST-Fertigstellungs-zeitpunkt")
    # Name machine number colums appropriately
    order_df.columns.values[25] = "1531"
    order_df.columns.values[26] = "1532"
    order_df.columns.values[27] = "1533"
    order_df.columns.values[28] = "1534"
    order_df.columns.values[29] = "1535"
    order_df.columns.values[30] = "1536"
    order_df.columns.values[31] = "1537"
    order_df.columns.values[32] = "1541"
    order_df.columns.values[33] = "1542"
    order_df.columns.values[34] = "1543"
    # Combine all machine numbers into one column
    order_df['selected_machine'] = ''
    order_df['selected_machine'] += np.where(
        order_df['1531'] == 'x', '1531,', '')
    order_df['selected_machine'] += np.where(
        order_df['1532'] == 'x', '1532,', '')
    order_df['selected_machine'] += np.where(
        order_df['1533'] == 'x', '1533,', '')
    order_df['selected_machine'] += np.where(
        order_df['1534'] == 'x', '1534,', '')
    order_df['selected_machine'] += np.where(
        order_df['1535'] == 'x', '1535,', '')
    order_df['selected_machine'] += np.where(
        order_df['1536'] == 'x', '1536,', '')
    order_df['selected_machine'] += np.where(
        order_df['1537'] == 'x', '1537,', '')
    order_df['selected_machine'] += np.where(
        order_df['1541'] == 'x', '1541,', '')
    order_df['selected_machine'] += np.where(
        order_df['1542'] == 'x', '1542,', '')
    order_df['selected_machine'] += np.where(
        order_df['1543'] == 'x', '1543', '')

    # Name first column to reference it for deletion
    order_df = order_df.rename(columns={order_df.columns[0]: 'Nichts'})
    order_df = order_df.drop('Nichts', axis=1)
    # Ignore first 14 rows since data starts at row 15
    order_df = order_df.drop(np.arange(13))
    order_df = order_df.reset_index(drop=True)
    # Only select the relevant columns
    order_df = order_df[['Fertigungsauf-tragsnummer',
                         'Artikelnummer',
                         'Auftragseingabe-zeitpunkt',
                         'Nummer Wickel-rohrmaschine',
                         'selected_machine',
                         'Werkzeug-nummer',
                         'Rüstzeit für WKZ/Materialwechsel',
                         'Rüstzeit für Coilwechsel',
                         'Maschinen-laufzeit',
                         'Dauer Handarbeit',
                         'Schichtmodell',
                         'spätester Fertigstellungszeitpunkt',
                         'Spätester Bearbeitungsbeginn',
                         'Berechneter Bearbei-tungsbeginn',
                         'Berechneter Fertigstellungs-zeitpunkt',
                         'PLAN-Bearbeitungs-beginn',
                         'PLAN-Fertigstellungs-zeitpunkt',
                         'IST- Bearbeitungs-beginn',
                         'IST-Fertigstellungs-zeitpunkt']]
    # Rename the columns into english
    order_df.rename(columns={'Fertigungsauf-tragsnummer': 'job',
                             'Artikelnummer': 'item',
                             'Auftragseingabe-zeitpunkt': 'order_release',
                             'Nummer Wickel-rohrmaschine': 'selected_machine',
                             'Maschinenangebot': 'machines',
                             'Werkzeug-nummer': 'tool',
                             'Rüstzeit für WKZ/Materialwechsel':
                                 'setuptime_material',
                             'Rüstzeit für Coilwechsel': 'setuptime_coil',
                             'Maschinen-laufzeit': 'duration_machine',
                             'Dauer Handarbeit': 'duration_manual',
                             'Schichtmodell': 'shift',
                             'spätester Fertigstellungszeitpunkt': 'deadline',
                             'Spätester Bearbeitungsbeginn':
                                 'latest_start',
                             'Berechneter Bearbei-tungsbeginn':
                                 'calculated_start',
                             'Berechneter Fertigstellungs-zeitpunkt':
                                 'calculated_end',
                             'PLAN-Bearbeitungs-beginn':
                                 'planned_start',
                             'PLAN-Fertigstellungs-zeitpunkt':
                                 'planned_end',
                             'IST- Bearbeitungs-beginn':
                                 'final_start',
                             'IST-Fertigstellungs-zeitpunkt':
                                 'final_end'},
                    inplace=True)
    order_df['order_release'] = pd.to_datetime(order_df['order_release'])
    order_df['deadline'] = pd.to_datetime(order_df['deadline'])
    order_df['duration_machine'] = order_df['duration_machine'].map(
        lambda x: datetime.timedelta(minutes=x))
    order_df['duration_manual'] = order_df['duration_manual'].map(
        lambda x: datetime.timedelta(minutes=x))
    order_df['setuptime_material'] = order_df['setuptime_material'].map(
        lambda x: datetime.timedelta(minutes=x))
    order_df['setuptime_coil'] = order_df['setuptime_coil'].map(
        lambda x: datetime.timedelta(minutes=x))
    return set_order_status(order_df)
