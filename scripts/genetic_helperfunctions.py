from shift import ShiftModel
import orders
import numpy as np
import datetime
import pandas as pd
import random
import copy

machineslist = [1531, 1532, 1533,1534, 1535, 1536, 1537,1541, 1542, 1543]
start = datetime.datetime(2022, 2, 27, 6, 0, 0)
#end = datetime.datetime(2022, 3, 4, 22, 0, 0)
end = datetime.datetime(2022, 2, 27, 22, 0, 0)

#resetting/initialising the dataframe using orders.py
def initializing_new_df():
    

    original_df = orders.get_westaflex_orders()

    original_df["duration"] = (original_df["setuptime_material"] + original_df["setuptime_coil"] + original_df["duration_machine"] + original_df["duration_manual"]).dt.seconds # am Ende überprüfen ob es klappt
    #df["chosen_machine"] = [0]*len(df)
    original_df["lateness"] = [0]*len(original_df)
    #
    original_df["calculated_setup_time"] = original_df["setup_time"] #um nachher das zu 0 werden zu lassen, welches nicht gebraucht wird
    #schauen, ob ich es schaffe, den df als globale varaible zu definieren um den aufruf in average lateness zu sparen

    #30 Einträge nur nutzen , für den Test
    original_df = original_df.reset_index(drop=True)
    original_df = original_df.tail(n=120)
    #nochmal überlegen ob das heir sinn ergibt
    #original_df.index = ids[:30]
    original_df = original_df.sort_index(ascending=True)
    
    
    
    
    
    return original_df


def create_helperframe():
        data = {
            "machineworkload": [0] * len(machineslist),
            "jobs" : [[],[],[],[],[],[],[],[],[],[]], # manuelle Eingabe wichtig, da sonst nur Kopien von einer List erstellt werden
        }

        helperframe = pd.DataFrame(data=data,index=machineslist)
        helperframe = helperframe.reset_index(drop=True)
        helperframe.index = machineslist
        
        return helperframe


def earliest_deadline_first(ids):
    
    init_df = initializing_new_df(ids)
    df = copy.deepcopy(init_df)
    
    #Pausenzeiten angeben
    '''plan_length_in_hours = abs((start-end).total_seconds()/3600)
    pauset_time_min = 45
    amount_of_pause_per_shift = 2
    amount_of_shifts_per_day = 2
    amount_of_days = plan_length_hours
    length_of_shifts = 8
    
    
    pauses_per_entity = plan_length_hours / (amount_of_shifts_per_day * amount_of_days * 4)
    
    '''
    
    
    #creating helperframe to determine the right machine which has to be used
    #
    helperframe = create_helperframe()
    id_start = df.index[0]
    #Ordering the jobs to the right machine from index 1 to end of df
    for i in range(id_start ,len(df)): 
        machine = 0
        
        
        
        #machines zum Tuple formatieren um Mimimum nehmen zu können
        included_keys = df["machines"].iloc[i].split(",")
        included_keys_list = list(map(int, included_keys ))
        included_keys_tuple = tuple(list(map(int, included_keys )))
        
        
        #machine_index
        minimum = min(helperframe.loc[included_keys_tuple,:]["machineworkload"])#berechnet die geringst Auslastung der ausgewählten Maschinen
        machines_index = helperframe.index[helperframe["machineworkload"] == minimum].tolist() # Maschine(n) die auf Basis der minimalen Auslastung gewählt wurden.List als Ausgabe
        
        #am i picking only from the subset of machines?
        if len(machines_index) > 1:
            machine = random.choice(machines_index)
        else:
            machine = machines_index[0]


        #Rest
        current_workload = int(helperframe.loc[machine]["machineworkload"])
        

        helperframe.at[machine, "machineworkload"] += df.iloc[i,:]["duration"]
        df.at[i,"selected_machine"] = machine
        
        if len(helperframe.loc[machine]["jobs"])>0:
            #hier müssen wir schauen welcher job zuletzt auf der maschine lief und die endzeit als startzeit wählen
            machine_jobs = helperframe.loc[machine]["jobs"] #Anzeigen der bisherigen Jobs
            last_job_id = machine_jobs[-1] # Die ID des letzten Jobs ausgeben, um den neuen an das Ende des alten anzuschließen
            df.at[i, "calculated_start"] = df.loc[last_job_id]["calculated_end"] + datetime.timedelta(seconds=current_workload)
        else:
            df.at[i, "calculated_start"] = start
        
        #if-statement einfügen um Pausenzeiten zu berücksichtigen. Genauso wie
        
        df.at[i, "calculated_end"] = df.loc[i]["calculated_start"] + datetime.timedelta(seconds=int(df.loc[i]["duration"]))
        df.at[i, "lateness"] = df.loc[i]["calculated_end"] - df.loc[i]["deadline"]

        helperframe.at[machine,"jobs"].append(i)
    
    
    for i in range(id_start, len(df)):
        
        
        #big_helperframe = helperframe.explode("jobs")
        
        current_machine = df.at[i,"selected_machine"]
        machine_jobslist = helperframe.at[current_machine,"jobs"]
        
        current_job_on_machine_index = machine_jobslist.index(i)#
        last_tool = "start"
        if current_job_on_machine_index > 0:
            last_job_on_machine_index = machine_jobslist.index(i) - 1
            last_job = machine_jobslist[last_job_on_machine_index]
            
            last_tool = df.at[last_job, "tool"]
        else:
            
            last_tool = "no tool"
        
        
        #setting the setuptime to zero, if we do not need any setup
        if df.loc[i]["tool"] == last_tool:
            df.at[i,"calculated_setup_time"] = 0
            
        
        

    return df           #hier muss helperframe für unsere heuristik stehen


def average_lateness(ids):#
    init_df = earliest_deadline_first(ids)
    lateness_df = copy.deepcopy(init_df)
    #Average lateness
    lateness_seconds = pd.to_timedelta(lateness_df["lateness"]).dt.total_seconds()
    #lösche Negative Einträge zu 0:
    lateness_seconds = lateness_seconds.apply(lambda x: x if x>=0 else 0)
    total_lateness = lateness_seconds.sum()
    average_lateness = total_lateness / len(lateness_df)
    
    return average_lateness

def makespan(ids):
    
    init_df =  earliest_deadline_first(ids)
    
    id_start = init_df.index[0]
    

    makespan_df = copy.deepcopy(init_df)

    for i in range (id_start, len(makespan_df)):
        if end<makespan_df.loc[i]["calculated_end"] and makespan_df.loc[i]["calculated_start"]<end:
            makespan_df.at[i,"duration"] = abs(makespan_df.iloc[i]["duration"]) - pd.to_timedelta(makespan_df.iloc[i]["calculated_end"] - end).total_seconds()
        
        if makespan_df.loc[i]["calculated_start"]>end:
            makespan_df.at[i,"duration"] = 0

    makespan_df["duration"] - pd.to_timedelta(makespan_df["calculated_setup_time"]).dt.total_seconds()
    makespan_df["duration"].apply(lambda x: 0 if x<0 else x)
    makespan = makespan_df["duration"].sum()
    
    
    return makespan