import simpy
import random
from datetime import datetime
import pandas as pd
import orders
from genetic_helperfunctions import makespan, average_lateness, machineslist, start, end
import json

def string_to_timestamp(datestring):
    return datetime.strptime(str(datestring), "%Y-%m-%d %H:%M:%S")

class Machine:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)
    
    def is_available(self, job):
        if self.machine.count == 0:
            availability = True
        else:
            availability = False
        return availability

    def run_job(self, job):
        release_time = string_to_timestamp(job["order_release"])
        current_time = datetime.fromtimestamp(self.env.now)
        diff_delay = max((release_time - current_time).total_seconds(),0)
        yield self.env.timeout(diff_delay)

        machine_request = self.machine.request()
        yield machine_request
        print(self.name," self.availability = False :",self.machine.capacity, self.machine.count)

        start = self.env.now
        job["calculated_start"] = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
        job["selected_machine"] = self.name
        print(f"Job {job['job']} on Machine {job['selected_machine']} starts at {job['calculated_start']}")
        yield self.env.timeout(job["duration_machine"].total_seconds()) # minutes to seconds
        job["calculated_end"] = datetime.fromtimestamp(self.env.now).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Job {job['job']} on Machine {job['selected_machine']} ends at {job['calculated_end']}")
        self.machine.release(machine_request)
        print(job['selected_machine']," self.availability = False :",self.machine.capacity, self.machine.count)

        start_time_comp = string_to_timestamp(job["calculated_start"])
        release_date_comp = string_to_timestamp(job["order_release"])
        end_time_comp = string_to_timestamp(job["calculated_end"])
        deadline_comp = string_to_timestamp(job["deadline"])
        
        if start_time_comp > release_date_comp:
            job["jobStartDelay"] = (start_time_comp - release_date_comp).total_seconds()
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

class MachineGroup:
    def __init__(self, env, group_name):
        self.env = env
        self.group_name = group_name
        self.machines = []
    
    def add_machine(self, machine):
        self.machines.append(machine)

    def get_available_machines(self, machines, job):
        available_machines = []
        for machine in self.machines:
            if machine.is_available(job):
                if grouping:
                    available_machines.append(machine)
                else:
                    if machine.name in machines:
                        available_machines.append(machine)
        return available_machines

    def schedule_job(self, job):
        if grouping:
            available_machines = self.get_available_machines(self.machines, job)
        else:
            possible_machines = str(job["selected_machine"]).split(",")
            available_machines = self.get_available_machines(possible_machines, job)

        # print("available_machines:",len(available_machines))
        if available_machines:
            chosen_machine = available_machines[0]
            self.env.process(chosen_machine.run_job(job))

class ManufacturingLayer:
    def __init__(self):
        self.machine_groups = []
    
    def add_machine_group(self, machine_group):
        self.machine_groups.append(machine_group)
    
    def schedule_job(self, job):
        if grouping:
            for machine_group in self.machine_groups:
                if machine_group.group_name == job["group"]:
                    machine_group.schedule_job(job)
                    break
        else:
            self.machine_groups[0].schedule_job(job)

class ProductionPlant:
    def __init__(self):
        self.manufacturing_layers = []
    
    def add_manufacturing_layer(self, manufacturing_layer):
        self.manufacturing_layers.append(manufacturing_layer)
    
    def schedule_jobs(self, joblist):
        # Create a job wait queue for each pair of ManufacturingLayers
        job_queues = [joblist]
        for i in range(len(self.manufacturing_layers) - 1):
            job_queues.append([])
        
        # Schedule jobs through each ManufacturingLayer
        for i, manufacturing_layer in enumerate(self.manufacturing_layers):
            for job in job_queues[i]:
                manufacturing_layer.schedule_job(job)
                # Add the job to the next job wait queue
                if i < len(self.manufacturing_layers) - 1:
                    job_queues[i + 1].append(job)
        
        # Return the output job wait queue (the one after the last ManufacturingLayer)
        return job_queues[-1]

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

def get_makespan(job_list):
    min_start = None
    max_end = None
    for job in job_list:
        if not min_start or string_to_timestamp(job["calculated_start"]) < min_start:
            min_start = string_to_timestamp(job["calculated_start"])
        if not max_end or string_to_timestamp(job["calculated_end"]) > max_end:
            max_end = string_to_timestamp(job["calculated_end"])
    return (max_end - min_start).total_seconds()

def main_ms(ids):
    df = orders.get_westaflex_orders()
    
    df = df.reindex(ids)
    print(df)
    job_list = df.to_dict(orient='records')

    ml1 = ManufacturingLayer()

    pp = ProductionPlant()
    pp.add_manufacturing_layer(ml1)
    
    env = simpy.Environment()

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

    output = pp.schedule_jobs(job_list)

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

    return makespans[0]

if __name__ == "__main__":
    df = orders.get_westaflex_orders()

    sorting_tech = "LJF"
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

    makespans = main_ms(ids)
    print(makespans)
