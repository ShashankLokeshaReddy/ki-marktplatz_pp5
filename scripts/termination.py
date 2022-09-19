import visualization
import pyomomachsched
from shift import ShiftModel

import datetime
import os
import pathlib

import numpy as np
import pandas as pd

# Current script directory
script_directory = pathlib.Path(__file__).parent.resolve()
# Default path of the order database excel file
default_database_path = os.path.join(script_directory, '..', 'data',
                                     "20220706_Auftragsdatenbank.xlsm")


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
    df[col_name] = pd.to_datetime(df[col_name], errors="coerce")
    return df


def get_orders(path: str = default_database_path) -> pd.DataFrame:
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
            job, item, order_release, machine, machine_selection, tool,
            setuptime_material, setuptime_coil, duration_machine,
            duration_hand, deadline, calculated_start, calculated_end,
            planned_start, planned_end, actual_start, actual_end
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
        order_df, "Berechneter Fertigstellungs-zeitpunkt"
    )
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
    order_df['machine_selection'] = ''
    order_df['machine_selection'] += np.where(
        order_df['1531'] == 'x', '1531,', '')
    order_df['machine_selection'] += np.where(
        order_df['1532'] == 'x', '1532,', '')
    order_df['machine_selection'] += np.where(
        order_df['1533'] == 'x', '1533,', '')
    order_df['machine_selection'] += np.where(
        order_df['1534'] == 'x', '1534,', '')
    order_df['machine_selection'] += np.where(
        order_df['1535'] == 'x', '1535,', '')
    order_df['machine_selection'] += np.where(
        order_df['1536'] == 'x', '1536,', '')
    order_df['machine_selection'] += np.where(
        order_df['1537'] == 'x', '1537,', '')
    order_df['machine_selection'] += np.where(
        order_df['1541'] == 'x', '1541,', '')
    order_df['machine_selection'] += np.where(
        order_df['1542'] == 'x', '1542,', '')
    order_df['machine_selection'] += np.where(
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
                         'machine_selection',
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
                             'Nummer Wickel-rohrmaschine': 'machine',
                             'Maschinenangebot': 'machine_selection',
                             'Werkzeug-nummer': 'tool',
                             'Rüstzeit für WKZ/Materialwechsel':
                                 'setuptime_material',
                             'Rüstzeit für Coilwechsel': 'setuptime_coil',
                             'Maschinen-laufzeit': 'duration_machine',
                             'Dauer Handarbeit': 'duration_hand',
                             'Schichtmodell': 'shift_model',
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
                                 'actual_start',
                             'IST-Fertigstellungs-zeitpunkt':
                                 'actual_end'},
                    inplace=True)
    order_df['order_release'] = pd.to_datetime(order_df['order_release'])
    order_df['duration_machine'] = order_df['duration_machine'].map(
        lambda x: datetime.timedelta(minutes=x))
    order_df['duration_hand'] = order_df['duration_hand'].map(
        lambda x: datetime.timedelta(minutes=x))
    order_df['setuptime_material'] = order_df['setuptime_material'].map(
        lambda x: datetime.timedelta(minutes=x))
    order_df['setuptime_coil'] = order_df['setuptime_coil'].map(
        lambda x: datetime.timedelta(minutes=x))
    return order_df


def calculate_end_time(start: datetime.datetime,
                       duration: int,
                       shift_model: str) -> datetime.datetime:
    """
    Calculates the time a job gets finished based on the given duration.

    Takes a start and a duration, and considers company holidays as well as
    operating shifts, to calculate the end time of the finished job and
    returns it.

    Parameters
    ----------
    start : datetime.datetime
        The start time of the job.
    duration : int
        The duration of the job in minutes.
    shift_model : str
        The shift model determines which hours are available for work.
        Possible shift models are:
            Flex, FlexS, Flex+S, W01S1, W01S3, W01YL, W011

    Returns
    -------
    datetime.datetime
        The end time of the job.
    """
    if isinstance(start, pd.Timestamp):
        start = start.to_pydatetime()
    elif isinstance(start, datetime.datetime):
        pass
    else:
        raise ValueError(
            'start parameter needs to be of type datetime.datetime or pandas.Timestamp')

    shifts = ShiftModel(start, shift_model)
    # Add the duration of the job to the current shift time
    current_shift_time = shifts.add_time(datetime.timedelta(minutes=duration))

    return current_shift_time


def calculate_setup_time(tool1: str, tool2: str) -> int:
    """
    Returns 15 if both given tools are not equal, otherwise returns 0.

    Takes two tool names as strings and returns a naive setup time calculation.
    If the same tool is reused for the next order, no setup time is required,
    otherwise a fixed 15 minutes is added to the overall run time.
    The strings are case insensitive and white spaces get removed.

    Parameters
    ----------
    tool1 : str
        Tool name as string e.g. 'A0 023'
    tool2 : str
        Tool name as string e.g. 'A0 023'

    Returns
    -------
    int
        setup time in minutes
    """
    tool1 = str(tool1)
    tool2 = str(tool2)
    # Remove whitespaces and make case insensitive comparison
    if tool1.casefold().replace(' ', '') == tool2.casefold().replace(' ', ''):
        setup_time = 0
    else:
        setup_time = 15
    return setup_time


# TODO: Rüstzeit erste Maschine?
# TODO: Startzeit current time?
def naive_termination(order_df, start, last_tool):
    """
    Calculates a simple termination from the given orders and returns it.

    Parameters
    ----------
    order_df: dataframe
        Orders in a dataframe containing the columns:
            machine, job, shift_model, order_release, duration_machine,
            setup_time
        Overwrites the values of following columns:
            calculated_start, calculated_end.
    start: datetime
        The start time of the naive termination calculation.
    last_tool: str
        The last tool name that has been used in the last job before the
        termination.

    Returns
    -------
    dataframe
        The orders with overwritten calculated_start and calculated_end.
    """
    # TODO: Currently, setup time gets added but it should be subtracted
    machines = order_df['machine'].astype(int).unique()
    order_df = order_df.assign(setup_time=0)
    # Für jede Maschine
    for machine in machines:
        df_machine = order_df[
            order_df['machine'].astype(int) == machine]
        timestamp = start
        # Entsprechend der Reihenfolge timestamps berechnen
        for index, row in df_machine.iterrows():
            order_num = row['job']
            shift_model = row['shift_model']

            # TODO: What about already running jobs? Or jobs that are finished?
            if timestamp < row['order_release']:
                timestamp = row['order_release']
            # Adjust timestamp to next shift start
            shifts = ShiftModel(timestamp, shift_model)
            timestamp = shifts.get_earliest_time(timestamp)

            order_df.loc[order_df['job'] == order_num,
                         ['calculated_start']] = timestamp
            tool = row['tool']
            setup_time = calculate_setup_time(tool, last_tool)
            order_df.loc[order_df['job'] == order_num,
                         ['setup_time']] = setup_time
            prod_time = row['duration_machine']
            if isinstance(prod_time, datetime.timedelta):
                prod_time = prod_time.total_seconds() / 60
            runtime = prod_time + setup_time
            timestamp = calculate_end_time(start=timestamp,
                                           duration=runtime,
                                           shift_model=shift_model)
            order_num = row['job']
            order_df.loc[order_df['job'] == order_num,
                         ['calculated_end']] = timestamp
            last_tool = tool
    return order_df


def _convert_date_to_datetime(date: str) -> datetime.datetime:
    """
    Converts string format dd.mm.yyyy to datetime object
    """
    if not isinstance(date, str):
        return datetime.datetime(0, 0, 0)
    if not date or date.lower() == 'nan':
        return datetime.datetime(0, 0, 0)
    if not date.count('.') == 2 or len(date) != 10:
        raise ValueError(f'{date} not expected format dd.mm.yyyy')
    # Turn date around to yyyy-mm-dd first
    date = date.split('.')
    if len(date[0]) == 4:
        # In format yyyy.mm.dd, so reverse list
        date.reverse()
    swapped_date = date[2] + '-' + date[1] + '-' + date[0]
    return datetime.datetime.fromisoformat(swapped_date)


def combine_orders(order_df, start):
    """
    Combines orders with the same item properties.
    """
    # TODO: FINISH THIS FUNCTION
    new_df = pd.DataFrame()
    start_week = start.isocalendar()[1]
    # Add all orders that have no start yet
    new_df.append(order_df[order_df['actual_start'].isnull()])
    # Add all orders that did not start before the planing week
    # TODO: Find way to convert string to datetime in row selection
    if not order_df[order_df['actual_start'].isnull()].empty:
        new_df.append(order_df[
            order_df['actual_start'].apply(_convert_date_to_datetime) > start])
    # Add all orders that have their latest start in the planing week
    new_df.append(
        order_df[_convert_date_to_datetime(
            order_df['latest_start']).isocalendar()[1] == start_week])
    # Add all orders that are currently running
    new_df.append(
        order_df[_convert_date_to_datetime(
            order_df['actual_start']) < start & _convert_date_to_datetime(
            order_df['actual_end']) > start])

    return new_df


if __name__ == "__main__":
    # Debugging
    df = get_orders()
    df.drop(index=df.index[:180], axis=0, inplace=True)
    # df = naive_termination(df, datetime.datetime(2022, 2, 27, 6, 0, 0), 'A0')
    # print(df[['order_release', 'machine', 'machine_selection', 'shift_model',
    #           'duration_machine', 'calculated_start', 'calculated_end',
    #           'setup_time']])
    df = pyomomachsched.opt_schedule(
        df, datetime.datetime(2022, 2, 27, 6, 0, 0), 'A0')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df[['order_release', 'machine', 'machine_selection', 'shift_model',
                  'duration_machine', 'calculated_start', 'calculated_end']])
    visualization.gantt(df)

    # print(calculate_end_time(start=datetime.datetime(
    #     2022, 4, 14, 14, 0, 0), duration=450, shift_model='FLEX'))
