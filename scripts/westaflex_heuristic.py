import pandas as pd
import pathlib
import os
import numpy as np

# Current script directory
project_directory = pathlib.Path(__file__).parent.parent.resolve()
# Default path of the order database excel file
default_database_path = os.path.join(project_directory, "data", "20220706_Auftragsdatenbank.xlsm")

def get_date(datetime_object):
    return str(datetime_object)[:11]

def combine_datetime_columns(df, col_name):
    default_time = '1999-01-01 00:00:00'
    df[col_name] = df[col_name].fillna(default_time).apply(get_date) + df.iloc[:, df.columns.get_loc(col_name)+1].fillna(default_time).astype(str)
    df[col_name] = pd.to_datetime(df[col_name])
    return df

def get_orders(path: str = default_database_path) -> pd.DataFrame:
    sheet_name = 'Datenbank_Auftragsdaten'
    order_df = pd.read_excel(path, sheet_name)  # Read file
    order_df = order_df.rename(columns=order_df.iloc[10])
    # Ignore first 14 rows since data starts at row 15
    order_df = order_df.drop(np.arange(13))
    order_df = order_df.reset_index(drop=True)
    # Combine date time columns
    order_df = combine_datetime_columns(order_df, 'Spätester Bearbeitungsbeginn')
    order_df = combine_datetime_columns(order_df, 'spätester Fertigstellungszeitpunkt') # assume spätester Fertigstellungszeitpunkt = spätester Fertigstellungstermin
    order_df = combine_datetime_columns(order_df, 'Berechneter Bearbei-tungsbeginn')
    order_df = combine_datetime_columns(order_df, 'Berechneter Fertigstellungs-zeitpunkt')
    order_df = combine_datetime_columns(order_df, 'PLAN-Bearbeitungs-beginn')
    order_df = combine_datetime_columns(order_df, 'PLAN-Fertigstellungs-zeitpunkt')
    order_df = combine_datetime_columns(order_df, 'IST- Bearbeitungs-beginn')
    order_df = combine_datetime_columns(order_df, 'IST-Fertigstellungs-zeitpunkt')
    # Name first column to reference it for deletion
    order_df = order_df.rename(columns={order_df.columns[0]: 'Nichts'})
    order_df = order_df.drop('Nichts', axis=1)
    # get all important columns
    order_df = order_df[['Fertigungsauf-tragsnummer', 'Spätester Bearbeitungsbeginn', 'spätester Fertigstellungszeitpunkt', 
        'Berechneter Bearbei-tungsbeginn', 'Berechneter Fertigstellungs-zeitpunkt', 'PLAN-Bearbeitungs-beginn',
        'PLAN-Fertigstellungs-zeitpunkt', 'IST- Bearbeitungs-beginn', 'IST-Fertigstellungs-zeitpunkt']]
    return order_df


def filter_planning_period(order_df, planning_period_start, planning_period_end):
    pass

# TODO remove finished orders
def set_order_status(order_df):
    order_df['Bearbeitungsstatus'] = 'Unbekannt'
    for idx in order_df.index:
        if order_df.loc[idx, 'Spätester Bearbeitungsbeginn'].year > 2000 and order_df.loc[idx, 'spätester Fertigstellungszeitpunkt'].year > 2000:
            order_df.loc[idx, 'Bearbeitungsstatus'] = 'Ungeplant'
        if order_df.loc[idx, 'Berechneter Fertigstellungs-zeitpunkt'].year > 2000 and order_df.loc[idx, 'Berechneter Bearbei-tungsbeginn'].year > 2000:
            order_df.loc[idx, 'Berechnet']
        if order_df.loc[idx, 'PLAN-Bearbeitungs-beginn'].year > 2000 and order_df.loc[idx, 'PLAN-Fertigstellungs-zeitpunkt'].year > 2000:
            order_df.loc[idx, 'Geplant']
        if order_df.loc[idx, 'IST-Fertigstellungs-zeitpunkt'].year > 2000:
            if order_df.loc[idx, 'IST- Bearbeitungs-beginn'].year < 2000:
                order_df.loc[idx, 'Bearbeitungsstatus'] = 'In Arbeit'
    return order_df
    

order_df = get_orders()
order_df = set_order_status(order_df)
print(order_df)
#print(order_df.head())