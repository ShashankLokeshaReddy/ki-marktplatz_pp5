from scripts.shift import ShiftModel
import visualization

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
            job, item, order_release, machine, tool, setuptime_material,
            setuptime_coil, duration_machine, duration_hand, deadline,
            calculated_start, calculated_end, planned_start, planned_end,
            actual_start, actual_end
    """
    sheet_name = 'Datenbank_Auftragsdaten'
    order_df = pd.read_excel(path, sheet_name)  # Read file
    order_df = order_df.rename(columns=order_df.iloc[10])
    # Name first column to reference it for deletion
    order_df = order_df.rename(columns={order_df.columns[0]: 'Nichts'})
    order_df = order_df.drop('Nichts', axis=1)
    # Ignore first 14 rows since data starts at row 15
    order_df = order_df.drop(np.arange(13))
    order_df = order_df.reset_index(drop=True)
    order_df = order_df[['Fertigungsauf-tragsnummer',
                         'Artikelnummer',
                         'Auftragseingabe-zeitpunkt',
                         'Nummer Wickel-rohrmaschine',
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
    order_df.rename(columns={'Fertigungsauf-tragsnummer': 'job',
                             'Artikelnummer': 'item',
                             'Auftragseingabe-zeitpunkt': 'order_release',
                             'Nummer Wickel-rohrmaschine': 'machine',
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
        start = datetime.datetime(start)
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
def calculate_timestamps(order_df, start, last_tool):
    """
    Calculates a simple termination from the given orders and returns it.
    """
    # TODO: Jobs shouldn't be able to start before their order comes in
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
            prod_time = int(row['duration_machine'])
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


# Debugging
# df = get_orders()
# print(df)
# df.drop(index=df.index[:180], axis=0, inplace=True)
# df = calculate_timestamps(df, datetime.datetime(2022, 2, 27, 6, 0, 0), 'A0')
# print(df[['job', 'machine', 'calculated_start', 'calculated_end', 'setup_time']])
# visualization.gantt(df)


# print(calculate_end_time(start=datetime.datetime(
#     2022, 4, 15, 0, 0, 0), duration=300, shift_model='FLEX'))
