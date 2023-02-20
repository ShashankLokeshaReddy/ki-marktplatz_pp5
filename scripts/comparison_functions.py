import visualization
import pyomomachsched
from shift import ShiftModel
import utility
import orders
import numpy as np
import datetime
import pandas as pd
import random
import time
import copy

start = datetime.datetime(2022, 2, 27, 6, 0, 0)
end = datetime.datetime(2022, 2, 27, 22, 0, 0)


def makespan_short(df):
#this algorithm can only be called once with the 

    #df["duration"] = df["duration"].abs()
    zero_entries = copy.deepcopy(df) 
    
    for i in range (len(df)):
        
        if end<zero_entries.loc[i]["calculated_end"] and zero_entries.loc[i]["calculated_start"]<end:
            zero_entries.at[i,"duration"] = abs(zero_entries.iloc[i]["duration"]) - pd.to_timedelta(zero_entries.iloc[i]["calculated_end"] - end).total_seconds()
        
        #if zero_entries.loc[i]["calculated_start"]>end:
        #    zero_entries.at[i,"duration"] = 0
    
    zero_entries["duration"] = zero_entries["duration"] - pd.to_timedelta(zero_entries["calculated_setup_time"]).dt.total_seconds()
    
    zero_entries["duration"].apply(lambda x: 0 if x<0 else x)
    
    makespan = zero_entries["duration"].sum()
    
    
    
    
    return makespan


def avg_lateness_short(df_short):
    df_lateness_short = copy.deepcopy(df_short)
    for i in range(len(df_short)):
        df_lateness_short.at[i, "lateness"] = df_lateness_short.loc[i]["calculated_end"] - df_lateness_short.loc[i]["deadline"]
    
    lateness_seconds = pd.to_timedelta(df_lateness_short["lateness"]).dt.total_seconds()
    #lösche Negative Einträge zu 0:
    lateness_seconds = lateness_seconds.apply(lambda x: x if x>=0 else 0)
    total_lateness = lateness_seconds.sum()
    average_lateness = total_lateness / len(df_lateness_short)
    return average_lateness