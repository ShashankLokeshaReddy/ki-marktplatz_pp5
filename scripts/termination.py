import datetime
import os
import pathlib

import numpy as np
import pandas as pd

# Current script directory
script_directory = pathlib.Path(__file__).parent.resolve()
# Default path of the order database excel file
default_database_path = os.path.join(script_directory,
                                     "20220706_Auftragsdatenbank.xlsm")


# TODO: Always current orders in table?
# What about orders that have already finished?
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
        Table of orders as pandas dataframe.
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
    order_df = order_df[['Fertigungsauf-tragsnummer', 'Artikelnummer',
                         'Auftragsmenge',  'Nummer Wickel-rohrmaschine',
                         'Werkzeug-nummer', 'Rüstzeit für WKZ/Materialwechsel',
                         'Rüstzeit für Coilwechsel', 'Maschinen-laufzeit',
                         'Fertigungszeit pro Mengeneinheit']]
    return order_df


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
    machines = order_df['Nummer Wickel-rohrmaschine'].astype(int).unique()
    order_df = order_df.assign(starttime=0)
    order_df = order_df.assign(endtime=0)
    order_df = order_df.assign(setup_time=0)
    # Für jede Maschine
    for machine in machines:
        df_machine = order_df[
            order_df['Nummer Wickel-rohrmaschine'].astype(int) == machine]
        timestamp = start
        # Entsprechend der Reihenfolge timestamps berechnen
        for index, row in df_machine.iterrows():
            order_num = row['Fertigungsauf-tragsnummer']
            if timestamp.hour > 18:  # Nächster Tag
                timestamp = datetime.datetime(timestamp.year, timestamp.month,
                                              timestamp.day+1, 6, 0, 0)
            print(order_num)
            order_df.loc[order_df['Fertigungsauf-tragsnummer'] == order_num,
                         ['starttime']] = timestamp
            tool = row['Werkzeug-nummer']
            setup_time = calculate_setup_time(tool, last_tool)
            order_df.loc[order_df['Fertigungsauf-tragsnummer'] == order_num,
                         ['setup_time']] = setup_time
            prod_time = int(row['Maschinen-laufzeit'])
            # try:
            #    prod_time = int(row['Maschinen-laufzeit'])
            # except Exception:
            # ?
            #    prod_time = 60
            runtime = prod_time + setup_time
            timestamp = timestamp + datetime.timedelta(minutes=runtime)
            order_num = row['Fertigungsauf-tragsnummer']
            order_df.loc[order_df['Fertigungsauf-tragsnummer'] == order_num,
                         ['endtime']] = timestamp
            last_tool = tool
    return order_df


# Debugging
#df = get_orders()
#df = calculate_timestamps(df, datetime.datetime(2022, 7, 20, 6, 0, 0), 'A0 2')
#df = df[['Nummer Wickel-rohrmaschine', 'starttime', 'endtime', 'setup_time']]
# print(df)
