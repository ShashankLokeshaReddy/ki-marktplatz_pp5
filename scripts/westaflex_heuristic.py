import pandas as pd
import pathlib
import os
import numpy as np
import datetime

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
    order_df = order_df[['Fertigungsauf-tragsnummer', 'Auftragseingabe-zeitpunkt', 'Spätester Bearbeitungsbeginn', 'Bearbeitungsdauer', 
        'Dauer Handarbeit', 'spätester Fertigstellungszeitpunkt', 'Berechneter Bearbei-tungsbeginn', 'Berechneter Fertigstellungs-zeitpunkt', 
        'PLAN-Bearbeitungs-beginn', 'PLAN-Fertigstellungs-zeitpunkt', 'IST- Bearbeitungs-beginn', 'IST-Fertigstellungs-zeitpunkt', 
        '1531', '1532', '1533', '1534', '1535', '1536', '1537', '1541', '1542', '1543', 'Rohrtyp', 'Werkzeug-nummer', 'Rüstzeit für WKZ/Materialwechsel']]
    order_df.rename(columns={'Fertigungsauf-tragsnummer': 'job',
            'Auftragseingabe-zeitpunkt': 'order_release',
            'Spätester Bearbeitungsbeginn': 'deadline_start',
            'spätester Fertigstellungszeitpunkt': 'deadline_end',
            'Berechneter Bearbei-tungsbeginn': 'calculated_start',
            'Berechneter Fertigstellungs-zeitpunkt': 'calculated_end',
            'PLAN-Bearbeitungs-beginn': 'planned_start',
            'PLAN-Fertigstellungs-zeitpunkt': 'planned_end',
            'IST- Bearbeitungs-beginn': 'final_start',
            'IST-Fertigstellungs-zeitpunkt': 'final_end',
            'Bearbeitungsdauer': 'machine_time',
            'Dauer Handarbeit': 'manual_time',
            'Rohrtyp': 'tube_type',
            'Werkzeug-nummer': 'tool',
            'Rüstzeit für WKZ/Materialwechsel': 'setuptime_material'
        }, inplace=True)
    return order_df

# TODO filter out jobs marked with "R"
# TODO remove jobs outside of planning_period
def filter_orders(order_def, planning_period_start, planning_period_end):
    return order_def

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

def compute_priority_list(order_df, priority_procedure):
    if priority_procedure == "first_come_first_serve":
        order_df['order_release'] = pd.to_datetime(order_df['order_release'])
        order_df.sort_values(by='order_release')
        return order_df['job'].tolist()
    else:
        raise Exception("Unknown priority procedure: " + priority_procedure)

def tool_setup_time(order_df, job1, job2):
    # setup time between orders job1 -> job2, returns setup time in minutes
    order2 = order_df.loc[order_df['job'] == job2]
    # if no previous job, return setup time for job
    if not job1:
        return order2['setuptime_material'].values[0]
    order1 = order_df.loc[order_df['job'] == job1]
    if order1['tube_type'].values[0] == order2['tube_type'].values[0] and order1['tool'].values[0] == order2['tool'].values[0]:
        return order2['setuptime_material'].values[0]
    else:
        return 0

def compute_machine_job_endtime(order_df, starttime, prev_job, job):
    # TODO Rüstzeit für Coilwechsel included in Rüstzeit für WKZ/Materialwechsel?
    setuptime_material = tool_setup_time(order_df, prev_job, job)
    order = order_df.loc[order_df['job'] == job]
    machine_time = order['machine_time'].values[0]
    manual_time = order['manual_time'].values[0]
    endtime = starttime + pd.DateOffset(minutes=setuptime_material) + pd.DateOffset(minutes=machine_time) + pd.DateOffset(minutes=manual_time)
    return endtime

def schedule_orders(order_df, order_machine_mapping, priority_list, planning_period_start, planning_period_end):
    # initiate machine jobs
    machine_endtime = {}
    machine_last_job = {}
    for machine in ('1531', '1532', '1533', '1534', '1535', '1536', '1537', '1541', '1542', '1543'):
        machine_endtime[machine] = planning_period_start
        machine_last_job[machine] = ''

    # add planned and running jobs
    for job in order_df.loc[order_df['status'] == 'in_work'].iterrows():
        assigned_machine = order_machine_mapping[job][0]
        if job['final_end'] > machine_endtime[assigned_machine]:
            machine_endtime[assigned_machine] = job['final_end']
            machine_last_job[assigned_machine] = job
    for job in order_df.loc[order_df['status'] == 'planned'].iterrows():
        assigned_machine = order_machine_mapping[job][0]
        if job['planned_end'] > machine_endtime[assigned_machine]:
            machine_endtime[assigned_machine] = job['planned_end']
            machine_last_job[assigned_machine] = job

    # iterate over prioritized jobs
    for job in priority_list:
        machine_tmp_id = ''
        machine_tmp_endtime = pd.Timestamp('NaT').to_pydatetime()
        # iterate over possible machines
        for machine in order_machine_mapping[job]:
            machine_curr_endtime = compute_machine_job_endtime(order_df, machine_endtime[machine], machine_last_job[machine], job)
            if pd.isnull(machine_tmp_endtime) or machine_curr_endtime < machine_tmp_endtime:
                machine_tmp_id = machine
                machine_tmp_endtime = machine_curr_endtime

        order_df.loc[(order_df['job'] == job), 'planned_start'] = machine_endtime[machine_tmp_id]
        order_df.loc[(order_df['job'] == job), 'planned_end'] = machine_tmp_endtime
        machine_endtime[machine_tmp_id] = machine_tmp_endtime
        machine_last_job[machine_tmp_id] = job

    return order_df

# scheduling parameters
planning_period_start = datetime.datetime(2020, 5, 17, 8, 0, 0)
planning_period_end = datetime.datetime(2020, 5, 24, 8, 0, 0)
priority_procedure = "first_come_first_serve"

order_df = get_orders()
order_df = filter_orders(order_df, planning_period_start, planning_period_end)
order_df = set_order_status(order_df)
order_machine_mapping = get_order_machine_mapping(order_df)
priority_list = compute_priority_list(order_df, priority_procedure)
order_df = schedule_orders(order_df, order_machine_mapping, priority_list, planning_period_start, planning_period_end)
print(order_df)
