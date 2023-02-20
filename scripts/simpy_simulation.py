import simpy
import random
from datetime import datetime
import pandas as pd
import pendulum
import orders
from genetic_helperfunctions import makespan, average_lateness, machineslist, start, end
import json
import time

def string_to_timestamp(datestring):
    return datetime.strptime(str(datestring), "%Y-%m-%d %H:%M:%S")

class Operator:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.operator = simpy.Resource(env, capacity=1)
    
    def is_available(self, job):
        # return self.operator.capacity > 0
        if self.operator.count == 0:
            availability = True
        else:
            availability = False
        return availability

class Machine:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)
    
    def is_available(self):
        # return self.machine.capacity > 0
        if self.machine.count == 0:
            availability = True
        else:
            availability = False
        return availability

class MachineGroup:
    def __init__(self, env, group_name):
        self.env = env
        self.group_name = group_name
        self.machines = []
        self.operators = []
    
    def add_machine(self, machine):
        self.machines.append(machine)

    def add_operator(self, operator):
        self.operators.append(operator)

    def get_available_machines(self, machines):
        available_machines = []
        for machine in self.machines:
            if machine.is_available():
                if grouping:
                    available_machines.append(machine)
                else:
                    if machine.name in machines:
                        available_machines.append(machine)
        return available_machines 

    def run_job(self, job):
        release_time = string_to_timestamp(job["order_release"]) # "2021-09-01 00:00:00"
        current_time = datetime.fromtimestamp(self.env.now)
        diff_delay = max((release_time - current_time).total_seconds(),0)
        yield self.env.timeout(diff_delay)
        if grouping:
            available_machines = self.get_available_machines(self.machines)
            duration_machine = job["duration_machine"] * 60 # minutes to seconds
        else:
            possible_machines = str(job["machines"]).split(",")
            available_machines = self.get_available_machines(possible_machines)
            duration_machine = job["duration_machine"].total_seconds()

        while not available_machines:
            yield self.env.timeout(1)
            if grouping:
                available_machines = [machine for machine in self.machines if machine.is_available()]
            else:
                available_machines = self.get_available_machines(possible_machines)

        chosen_machine = available_machines[0]#random.choice(available_machines)
        if not chosen_machine.name in possible_machines:
            print("Wrong machine allocated")
            return

        machine_request = chosen_machine.machine.request()
        yield machine_request
        # print(chosen_machine.name," self.availability = False :",chosen_machine.machine.capacity, chosen_machine.machine.count)

        start = self.env.now
        job["calculated_start"] = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
        job["selected_machine"] = chosen_machine.name
        # print(f"Job {job['job']} on Machine {job['selected_machine']} starts at {job['calculated_start']}")
         
        yield self.env.timeout(duration_machine)
        job["calculated_end"] = datetime.fromtimestamp(self.env.now).strftime("%Y-%m-%d %H:%M:%S")
        # print(f"Job {job['job']} on Machine {job['selected_machine']} ends at {job['calculated_end']}")
        chosen_machine.machine.release(machine_request)
        # print(job['selected_machine']," self.availability = False :",chosen_machine.machine.capacity, chosen_machine.machine.count)

        start_time_comp = string_to_timestamp(job["calculated_start"])
        end_time_comp = string_to_timestamp(job["calculated_end"])
        deadline_comp = string_to_timestamp(job["deadline"])
        
        if start_time_comp > release_time:
            job["jobStartDelay"] = (start_time_comp - release_time).total_seconds()
            job_start_delays.append(job["jobStartDelay"])
        
        if end_time_comp > deadline_comp:
            job["jobEndDelay"] = (end_time_comp - deadline_comp).total_seconds()
            deadlin_exceeded.append(job["jobEndDelay"])

        job["order_release"] = job["order_release"].strftime('%Y-%m-%d %H:%M:%S')
        job["setuptime_material"] = job["setuptime_material"].total_seconds()
        job["setuptime_coil"] = job["setuptime_coil"].total_seconds()
        job["duration_machine"] = job["duration_machine"].total_seconds()
        job["duration_manual"] = job["duration_manual"].total_seconds()
        job["deadline"] = job["deadline"].strftime('%Y-%m-%d %H:%M:%S')
        job["latest_start"] = job["latest_start"].strftime('%Y-%m-%d %H:%M:%S')
        job["setup_time"] = job["setup_time"].total_seconds()
        job["status"] = job["status"].value

    def schedule_job(self, sublist):
        for job in sublist:
            self.env.process(self.run_job(job))          

class ManufacturingLayer:
    def __init__(self):
        self.machine_groups = []
    
    def add_machine_group(self, machine_group):
        self.machine_groups.append(machine_group)
    
    def schedule_job(self, joblist):
        if grouping:
            group_dict = {}
            for job in joblist:
                group = job['group']
                if group in group_dict:
                    group_dict[group].append(job)
                else:
                    group_dict[group] = [job]

            for machine_group in self.machine_groups:
                for group, sublist in group_dict.items():
                    if machine_group.group_name == group:
                        machine_group.schedule_job(sublist)
        
        else:
            self.machine_groups[0].schedule_job(joblist)

class ProductionPlant:
    def __init__(self):
        self.manufacturing_layers = []
    
    def add_manufacturing_layer(self, manufacturing_layer):
        self.manufacturing_layers.append(manufacturing_layer)    

def get_makespan(job_list):
    min_start = None
    max_end = None
    for job in job_list:
        if not min_start or string_to_timestamp(job["calculated_start"]) < min_start:
            min_start = string_to_timestamp(job["calculated_start"])
        if not max_end or string_to_timestamp(job["calculated_end"]) > max_end:
            max_end = string_to_timestamp(job["calculated_end"])
    return (max_end - min_start).total_seconds()

grouping = False
job_start_delays = []
deadlin_exceeded = []
total_job_start_delays = []
total_deadlin_exceeded = []
makespans = []

def delete_all_elements(my_list):
    for i in range(len(my_list) - 1, -1, -1):
        del my_list[i]
    return my_list

def main(ids):
    starttime = time.time()
    print("Simpy Simulation Start")
    df = orders.get_westaflex_orders()
    # df = pd.DataFrame(data, index=ids)
    df = df.reindex(ids)
    min_val = df['order_release'].min()
    job_list = df.to_dict(orient='records')

    ml1 = ManufacturingLayer()

    pp = ProductionPlant()
    pp.add_manufacturing_layer(ml1)
    dt = datetime(1970, 1, 1, 1, 0, 0)
    unix_time = int((dt - datetime(1970, 1, 1)).total_seconds())
    
    for i, manufacturing_layer in enumerate(pp.manufacturing_layers):
        env = simpy.Environment(initial_time=0)
        # env.advance(unix_time)
        m0 = Machine(env, "1531")
        m1 = Machine(env, "1532")
        m2 = Machine(env, "1533")
        m3 = Machine(env, "1534")
        m4 = Machine(env, "1535")
        m5 = Machine(env, "1536")
        m6 = Machine(env, "1537")
        m7 = Machine(env, "1541")
        m8 = Machine(env, "1542")
        m9 = Machine(env, "1543")

        mg1 = MachineGroup(env, "group1")
        mg1.add_machine(m0)
        mg1.add_machine(m1)
        mg1.add_machine(m2)
        mg1.add_machine(m3)
        mg1.add_machine(m4)
        mg1.add_machine(m5)
        mg1.add_machine(m6)
        mg1.add_machine(m7)
        mg1.add_machine(m8)
        mg1.add_machine(m9)

        ml1.add_machine_group(mg1)

        manufacturing_layer.schedule_job(job_list)
        env.run()
        print("Deadline exceeded for these many jobs: ", len(deadlin_exceeded))
        print("Sum of deadline delays: ", sum(deadlin_exceeded))
        print("Start delay for these many jobs: ", len(job_start_delays))
        print("Sum of job start delays: ", sum(job_start_delays))
        makespan = get_makespan(job_list)
        makespans.append(makespan)
        print("Makespan: ", makespan)

        # Do this for the next manufacturing layer
        if grouping:
            for job in job_list:
                job["selected_machine"] = ""
                job["order_release"] = job["calculated_end"]
                job["calculated_start"] = ""
                job["calculated_end"] = ""      
                job["jobStartDelay"] = ""
                job["jobEndDelay"] = ""

        total_job_start_delays.append(job_start_delays)
        total_deadlin_exceeded.append(deadlin_exceeded)
        delete_all_elements(job_start_delays)
        delete_all_elements(deadlin_exceeded)

    endtime = time.time()
    print("Simpy Simulation End")
    print("Simpy Simulation Time:",endtime - starttime)
    return makespans[0]

if __name__ == "__main__":
    df = orders.get_westaflex_orders()

    sorting_tech = "deadline"
    # # baseline approaches, presorts the joblist
    if sorting_tech == "SJF":
        df = df.sort_values(by='duration_machine')
        ids = list(df.index)
    elif sorting_tech == "LJF":
        df = df.sort_values(by='duration_machine', ascending=False)
        ids = list(df.index)
    elif sorting_tech == "deadline":
        df = df.sort_values(by='deadline')
        ids = list(df.index)
    elif sorting_tech == "releasedate":
        df = df.sort_values(by='order_release')
        ids = list(df.index)
    elif sorting_tech == "random":
        ids = df.sample(frac=1, random_state=42).index.to_list()

    makespans = main(ids)
