import pandas as pd
import numpy as np
import pathlib
import datetime
import os

script_directory = pathlib.Path(__file__).parent.resolve()

#TODO: Always current orders in table? What about orders that have already finished?
def get_orders(path = os.path.join(script_directory, "20220706_Auftragsdatenbank.xlsm")):
    """Opens an orderdatabase excel document to read orders and return them as a pandas dataframe.
    """
    sheet_name = 'Datenbank_Auftragsdaten'
    df = pd.read_excel(path, sheet_name) # Read file
    df = df.rename(columns=df.iloc[10]) #
    df = df.rename(columns={df.columns[0]:'Nichts'}) # Name first column to reference it for deletion
    df = df.drop('Nichts', axis=1)
    df = df.drop(np.arange(13)) # Ignore first 14 rows since data starts at row 15
    df = df.reset_index(drop=True)
    df = df[['Fertigungsauf-tragsnummer', 'Artikelnummer', 
            'Auftragsmenge',  'Nummer Wickel-rohrmaschine', 
            'Werkzeug-nummer', 'Rüstzeit für WKZ/Materialwechsel', 
            'Rüstzeit für Coilwechsel', 'Maschinen-laufzeit', 'Fertigungszeit pro Mengeneinheit']]
    return df

def calculate_setup_time(tool1, tool2):
    """Naive setup time calculation. If the same tool is reused for the next order, no setup time is required, otherwise
    a fixed 15 minutes is added to the overall run time.
    """
    if tool1 == tool2:
        setup_time = 0
    else:
        setup_time = 15
    return setup_time

#TODO: Rüstzeit erste Maschine?
#TODO: Startzeit current time?
def calculate_timestamps(df, start, last_tool):
    """Calculates a simple termination from the given orders. 
    """
    machines = df['Nummer Wickel-rohrmaschine'].astype(int).unique()
    df = df.assign(starttime=0)
    df = df.assign(endtime=0)
    df = df.assign(setup_time=0)
    # Für jede Maschine 
    for machine in machines:
        df_machine = df[df['Nummer Wickel-rohrmaschine'].astype(int) == machine]
        timestamp = start
        # Entsprechend der Reihenfolge timestamps berechnen
        for index, row in df_machine.iterrows():
            order_num = row['Fertigungsauf-tragsnummer']
            if timestamp.hour > 18: # Nächster Tag
                timestamp = datetime.datetime(timestamp.year, timestamp.month, timestamp.day+1, 6, 0, 0)
            print(order_num)
            df.loc[df['Fertigungsauf-tragsnummer'] == order_num, ['starttime']] = timestamp
            tool = row['Werkzeug-nummer']
            setup_time = calculate_setup_time(tool, last_tool)
            df.loc[df['Fertigungsauf-tragsnummer'] == order_num, ['setup_time']] = setup_time
            try:
                prod_time = int(row['Maschinen-laufzeit'])
            except:
                # ?
                prod_time = 60
            runtime = prod_time + setup_time
            timestamp = timestamp + datetime.timedelta(minutes=runtime)
            order_num = row['Fertigungsauf-tragsnummer']
            df.loc[df['Fertigungsauf-tragsnummer'] == order_num, ['endtime']] = timestamp
            last_tool = tool
    return df

df = get_orders()
#print(df)
df = calculate_timestamps(df, datetime.datetime(2022, 7, 20, 6, 0, 0), 'A0 023')
df = df[['Nummer Wickel-rohrmaschine', 'starttime', 'endtime', 'setup_time']]
print(df)