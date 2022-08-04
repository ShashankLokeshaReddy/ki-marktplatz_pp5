import pandas as pd
import pathlib
import os
import numpy as np

# project root path
PROJECT_PATH = pathlib.Path(__file__).parent.parent.resolve()
# path to data source file
DATA_SOURCE_PATH = os.path.join(PROJECT_PATH, "data", "20220706_Auftragsdatenbank.xlsm")
# sheet of source file containing database
DATA_SOURCE_SHEET = 'Datenbank_Auftragsdaten'

def get_date(datetime_object):
    return str(datetime_object)[:11]

def combine_datetime_columns(df, col_name):
    df[col_name] = df[col_name].apply(get_date) + df.iloc[:, df.columns.get_loc(col_name)+1].astype(str)
    df[col_name] = pd.to_datetime(df[col_name], errors='coerce')
    a = df[col_name]
    return df

def get_orders() -> pd.DataFrame:
    # Read file
    order_df = pd.read_excel(DATA_SOURCE_PATH, DATA_SOURCE_SHEET)  
    # Rename columns after sheet header
    order_df = order_df.rename(columns=order_df.iloc[10])
    # Ignore first 14 rows since data starts at row 15
    order_df = order_df.drop(np.arange(13))
    order_df = order_df.reset_index(drop=True)
    # Combine separate date time columns to datetime
    order_df = combine_datetime_columns(order_df, 'Spätester Bearbeitungsbeginn')
    order_df = combine_datetime_columns(order_df, 'spätester Fertigstellungszeitpunkt')
    order_df = combine_datetime_columns(order_df, 'Berechneter Bearbei-tungsbeginn')
    order_df = combine_datetime_columns(order_df, 'Berechneter Fertigstellungs-zeitpunkt')
    order_df = combine_datetime_columns(order_df, 'PLAN-Bearbeitungs-beginn')
    order_df = combine_datetime_columns(order_df, 'PLAN-Fertigstellungs-zeitpunkt')
    order_df = combine_datetime_columns(order_df, 'IST- Bearbeitungs-beginn')
    order_df = combine_datetime_columns(order_df, 'IST-Fertigstellungs-zeitpunkt')
    # Name machine number colums appropriately
    order_df.columns.values[25] = '1531'
    order_df.columns.values[26] = '1532'
    order_df.columns.values[27] = '1533'
    order_df.columns.values[28] = '1534'
    order_df.columns.values[29] = '1535'
    order_df.columns.values[30] = '1536'
    order_df.columns.values[31] = '1537'
    order_df.columns.values[32] = '1541'
    order_df.columns.values[33] = '1542'
    order_df.columns.values[34] = '1543'
    # Name first column to reference it for deletion
    order_df = order_df.rename(columns={order_df.columns[0]: 'Nichts'})
    order_df = order_df.drop('Nichts', axis=1)
    # get all important columns and rename them
    order_df = order_df[['Fertigungsauf-tragsnummer', 'Auftragseingabe-zeitpunkt', 'Spätester Bearbeitungsbeginn', 'spätester Fertigstellungszeitpunkt', 
        'Berechneter Bearbei-tungsbeginn', 'Berechneter Fertigstellungs-zeitpunkt', 'PLAN-Bearbeitungs-beginn',
        'PLAN-Fertigstellungs-zeitpunkt', 'IST- Bearbeitungs-beginn', 'IST-Fertigstellungs-zeitpunkt', 
        '1531', '1532', '1533', '1534', '1535', '1536', '1537', '1541', '1542', '1543', 'Rohrtyp', 'Werkzeug-nummer']]
    order_df.rename(columns={'Fertigungsauf-tragsnummer': 'job',
            'Auftragseingabe-zeitpunkt': 'order_release',
            'Spätester Bearbeitungsbeginn': 'deadline_start',
            'spätester Fertigstellungszeitpunkt': 'deadline_end',
            'Berechneter Bearbei-tungsbeginn': 'calculated_start',
            'Berechneter Fertigstellungs-zeitpunkt': 'calculated_end',
            'PLAN-Bearbeitungs-beginn': 'planned_start',
            'PLAN-Fertigstellungs-zeitpunkt': 'planned_end',
            'IST- Bearbeitungs-beginn': 'final_start',
            'IST-Fertigstellungs-zeitpunkt': 'final_end'
        }, inplace=True)
    return order_df

def set_order_status(order_df):
    # set order status according to timestamps
    order_df['status'] = 'unknown'
    for idx in order_df.index:
        if not pd.isnull(order_df.loc[idx, 'deadline_start']) and not pd.isnull(order_df.loc[idx, 'deadline_end']):
            order_df.loc[idx, 'status'] = 'unplanned'
        if not pd.isnull(order_df.loc[idx, 'calculated_start']) and not pd.isnull(order_df.loc[idx, 'calculated_end']):
            order_df.loc[idx, 'status'] = 'calculated'
        if not pd.isnull(order_df.loc[idx, 'planned_start']) and not pd.isnull(order_df.loc[idx, 'planned_end']):
            order_df.loc[idx, 'status'] = 'planned'
        if not pd.isnull(order_df.loc[idx, 'final_start']):
            order_df.loc[idx, 'status'] = 'in_work'
    # remove orders that are already finished
    order_df = order_df.drop(order_df[order_df['final_end'] == pd.NaT].index)
    # TODO compute final_end for orders in_work, where this is not given (order is finished in future)
    return order_df

def get_order_machine_mapping(order_df):
    order_machine_mapping = {}
    for _, row in order_df.iterrows():
        auftrag_nr = row['job']
        auftrag_machine_list = []
        if row['1531'] == 'x':
            auftrag_machine_list.append('1531')
        if row['1532'] == 'x':
            auftrag_machine_list.append('1532')
        if row['1533'] == 'x':
            auftrag_machine_list.append('1533')
        if row['1534'] == 'x':
            auftrag_machine_list.append('1534')
        if row['1535'] == 'x':
            auftrag_machine_list.append('1535')
        if row['1536'] == 'x':
            auftrag_machine_list.append('1536')
        if row['1537'] == 'x':
            auftrag_machine_list.append('1537')
        if row['1541'] == 'x':
            auftrag_machine_list.append('1541')            
        if row['1542'] == 'x':
            auftrag_machine_list.append('1542')       
        if row['1543'] == 'x':
            auftrag_machine_list.append('1543')    
        order_machine_mapping[auftrag_nr] = auftrag_machine_list
    return order_machine_mapping

def compute_priority_list(order_df):
    # first come first serve
    order_df['Auftragseingabe-zeitpunkt'] = pd.to_datetime(order_df['Auftragseingabe-zeitpunkt'])
    order_df.sort_values(by='Auftragseingabe-zeitpunkt')
    return order_df['job'].tolist()

order_df = get_orders()
# TODO filter out jobs marked with "R"
# TODO planning timespan given or take next as since now?
    # when is order before and after planning timespan?
        # remove them
order_df = set_order_status(order_df)
order_machine_mapping = get_order_machine_mapping(order_df)
priority_list = compute_priority_list(order_df)
print(priority_list)
