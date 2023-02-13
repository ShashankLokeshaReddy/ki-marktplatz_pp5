from shift import ShiftModel
import utility
import orders
import numpy as np
import datetime
import pandas as pd
from genetic_helperfunctions import initializing_new_df, create_helperframe

import copy



def string_to_list(x):
    y = x.split(",")
    x = list(map(int, y))
    return x

def heuristic(machineslist, start):
    #Weise jeder Maschine die als erstes wieder frei ist den nächsten Job zu, dies ist allerdings nicht optimierbar durch einen genetischen Algorithmus, denke ich
    
    df = initializing_new_df()
    helperframe = create_helperframe()
    
   
    df["machinecount"] = np.nan
    #Die Jobs nach der Anzahl der Möglichen Maschinen, auf welche sie bearbeitet werden können sortieren
    for i in range (len(df)):
        df.at[i,"machinecount"] = len(df.machines.iloc[i])
        '''for j in range (len(machineslist)):
            jobs = helperframe.jobs
            jobframe = pd.DataFrame(jobs)
            #Prüfe wie viele andere Maschinen dieser Job hat
            for job in jobframe.jobs:
                len(df.machines.iloc[job])'''
    df = df.sort_values('machinecount')
   
    #In den Helperframe für die einzelnen Maschinen die maximal mögliche Bearbeitungszeit eintragen

    #getting the job index
    
    
    #df.machines = df.machines.astype(str)
    #df.machines = df.machines.map(string_to_list)
   
    #df.machines = df.machines.apply(string_to_list)
    df.machines = df.machines.apply(string_to_list)
    big_df = df.explode("machines")
    

    possible_job_duration = []
    for machine in machineslist:
        jobs_for_machine = big_df.job[big_df.machines == machine] # welche Jobs können auf der Maschine laufen?
        amount_of_jobs = len(jobs_for_machine)
        possible_job_duration_on_machine = jobs_for_machine.sum()
        possible_job_duration.append(possible_job_duration_on_machine)



    helperframe["possible_duration"] = possible_job_duration

    helperframe = helperframe.sort_values("possible_duration")
    
    

    #Von oben nach unten im df immer die Maschine mit der geringsten möglichen Auslastung auswählen
        
    df = df.reset_index(drop=True)

    ranks = [x for x in range(1,11)]
    machine_ranking = pd.DataFrame(data = {'rank': ranks, 'machine': helperframe.index})
    for i in range(len(df)):
        possible_machines_list = df.loc[i]["machines"]
        
        possible_machines_rank = machine_ranking[machine_ranking.machine.isin(possible_machines_list)]
        possible_machines_rank = possible_machines_rank["rank"].tolist()
        
        chosen_machine = machine_ranking.machine.loc[possible_machines_rank[0]-1] #Wähle also die Maschine, die die geringste maximale Asulastung hat
        
        #Nun ordne die Aufträge entsprechend zu
        
        #Rest
        current_workload = int(helperframe.loc[chosen_machine]["machineworkload"])
            

        helperframe.at[chosen_machine, "machineworkload"] += df.iloc[i,:]["duration"]
        
        df.at[i,"selected_machine"] = chosen_machine

        if len(helperframe.loc[chosen_machine]["jobs"])>0:
            #hier müssen wir schauen welcher job zuletzt auf der maschine lief und die endzeit als startzeit wählen
            machine_jobs = helperframe.loc[chosen_machine]["jobs"] #Anzeigen der bisherigen Jobs
            
            last_job_id = machine_jobs[-1] # Die ID des letzten Jobs ausgeben, um den neuen an das Ende des alten anzuschließen
            
            df.at[i, "calculated_start"] = df.loc[last_job_id]["calculated_end"] + datetime.timedelta(seconds=current_workload)
        else:
            df.at[i, "calculated_start"] = start
        
        
            #if-statement einfügen um Pausenzeiten zu berücksichtigen. Genauso wie
            
        df.at[i, "calculated_end"] = df.loc[i]["calculated_start"] + datetime.timedelta(seconds=int(df.loc[i]["duration"]))
        df.at[i, "lateness"] = df.loc[i]["calculated_end"] - df.loc[i]["deadline"]

        helperframe.at[chosen_machine,"jobs"].append(i)
        
            
    return df
    #mögliche erweiterungen: falls jobs sehr lange dauern mit einbeziehen