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
    df[col_name] = df[col_name].fillna('').apply(get_date) + df.iloc[:, df.columns.get_loc(col_name)+1].fillna('').astype(str)
    return df

def get_orders(path: str = default_database_path) -> pd.DataFrame:
    sheet_name = 'Datenbank_Auftragsdaten'
    order_df = pd.read_excel(path, sheet_name)  # Read file
    order_df = order_df.rename(columns=order_df.iloc[10])
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
    # Ignore first 14 rows since data starts at row 15
    order_df = order_df.drop(np.arange(13))
    order_df = order_df.reset_index(drop=True)
    order_df = order_df[['Fertigungsauf-tragsnummer', 'Spätester Bearbeitungsbeginn', 'spätester Fertigstellungszeitpunkt', 
        'Berechneter Bearbei-tungsbeginn', 'Berechneter Fertigstellungs-zeitpunkt', 'PLAN-Bearbeitungs-beginn',
        'PLAN-Fertigstellungs-zeitpunkt', 'IST- Bearbeitungs-beginn', 'IST-Fertigstellungs-zeitpunkt']]
    return order_df


def filter_planning_period(order_df, planning_period_start, planning_period_end):
    pass

def set_order_status(order_df):
    order_df['Bearbeitungsstatus'] = 'Unbekannt'
    for row in order_df.itertuples():
        pass


order_df = get_orders()
#print(order_df)
#print(order_df.head())