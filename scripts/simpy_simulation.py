import simpy
import random
from datetime import datetime
import pandas as pd
from pandas import Timestamp, Timedelta
import pendulum
import orders
from genetic_helperfunctions import makespan, average_lateness, machineslist, start, end
import json
import csv
import time
import collections

logging = False
max_machine_duration_flag = [False]
max_machine_duration_default = 604800.0
max_machine_duration = [max_machine_duration_default]
iteration_start_time = [0]
job_start_delays = []
deadlin_exceeded = []
total_job_start_delays = []
total_deadlin_exceeded = []
makespans = []
makespans_cur_iter = []
scheduled_jobs = []
scheduled_jobs_in_cur_iter = []

def string_to_timestamp(datestring):
    return datetime.strptime(str(datestring), "%Y-%m-%d %H:%M:%S")

class Operator:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.operator = simpy.Resource(env, capacity=1)
        self.occupancy = 0
    
    def is_available(self):
        if self.operator.count == 0:
            availability = True
        else:
            availability = False
        return availability

class Postprocessor:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.postprocessor = simpy.Resource(env, capacity=1)
    
    def is_available(self):
        if self.postprocessor.count == 0:
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
        self.postprocessors = []
    
    def add_machine(self, machine):
        self.machines.append(machine)

    def add_operator(self, operator):
        self.operators.append(operator)

    def add_postprocessor(self, postprocessor):
        self.postprocessors.append(postprocessor)

class ManufacturingLayer:
    def __init__(self):
        self.machine_groups = []
        self.env = None
    
    def add_machine_group(self, machine_group):
        self.machine_groups.append(machine_group)
    
    def get_available_resources(self, machines):
        available_resources = []
        for machine_group in self.machine_groups:
            for machine in machine_group.machines:
                if machine.is_available():
                    if machine.name in machines:
                        for operator in machine_group.operators:
                            if operator.is_available():
                                for postprocessor in machine_group.postprocessors:
                                    if postprocessor.is_available():
                                        temp_dict = {"machine":machine, "operator":operator, "postprocessor":postprocessor}
                                        available_resources.append(temp_dict)
        return available_resources

    def run_job(self, job):
        release_time = string_to_timestamp(job["order_release"]) # "2021-09-01 00:00:00"
        earliest_prod_start_time = self.env.now
        current_time = datetime.fromtimestamp(self.env.now)
        if logging:
            print(current_time)
        diff_delay = max((release_time - current_time).total_seconds(),0)
        yield self.env.timeout(diff_delay)
        possible_machines = str(job["machines"]).split(",")
        available_resources = self.get_available_resources(possible_machines)
        duration_machine = job["duration_machine"].total_seconds()
        duration_manual = job["duration_manual"].total_seconds()

        while not available_resources:
            yield self.env.timeout(60)
            available_resources = self.get_available_resources(possible_machines)

        chosen_resource = available_resources[0] # random.choice(available_resources)
        chosen_machine = chosen_resource["machine"]
        chosen_operator = chosen_resource["operator"]
        chosen_postprocessor = chosen_resource["postprocessor"]
        if not chosen_machine.name in possible_machines:
            print("Wrong machine allocated")
            return
        if logging:
            print(current_time)
            print("max_machine_duration",(self.env.now + job["duration_machine"].total_seconds())/max_machine_duration_default, (earliest_prod_start_time + max_machine_duration[0])/max_machine_duration_default)
        if ((self.env.now + job["duration_machine"].total_seconds()) > (earliest_prod_start_time + max_machine_duration[0])):
            if max_machine_duration[0] == max_machine_duration_default and not max_machine_duration_flag[0]:
                print(self.env.now,"production duration exceeded for the job ", job["job"])
                return
            else:
                new_max_machine_duration = self.env.now + job["duration_machine"].total_seconds() - earliest_prod_start_time #, 1.1*max_machine_duration[0])
                delete_all_elements(max_machine_duration)
                max_machine_duration.append(new_max_machine_duration)
                delete_all_elements(max_machine_duration_flag)
                max_machine_duration_flag.append(False)

        # Check if operator occupany is above 90%
        if chosen_operator.occupancy > 0.9:
            yield self.env.timeout(duration_manual)

        machine_request = chosen_machine.machine.request()
        yield machine_request

        # Increment operator occupancy upon requesting new machine
        chosen_operator.occupancy = chosen_operator.occupancy + duration_manual/duration_machine
        # Mandatory setup times for every job
        yield self.env.timeout(job["setuptime_material"].total_seconds())
        yield self.env.timeout(job["setuptime_coil"].total_seconds())

        start = self.env.now
        job["final_start"] = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
        job["selected_machine"] = chosen_machine.name
        if logging:
            print(f"Job {job['job']} on Machine {job['selected_machine']} starts at {job['final_start']}")
         
        yield self.env.timeout(duration_machine)
        job["final_end"] = datetime.fromtimestamp(self.env.now).strftime("%Y-%m-%d %H:%M:%S")
        job["duration_machine"] = string_to_timestamp(job["final_end"]) - string_to_timestamp(job["final_start"])

        if logging:
            print(f"Job {job['job']} on Machine {job['selected_machine']} ends at {job['final_end']}")
        chosen_machine.machine.release(machine_request)

        # Decrement operator occupancy upon requesting new machine
        chosen_operator.occupancy = chosen_operator.occupancy - duration_manual/duration_machine

        postprocessor_request = chosen_postprocessor.postprocessor.request()
        yield postprocessor_request
        # TODO: Is timeout needed here?
        # yield self.env.timeout(duration_machine)
        chosen_postprocessor.postprocessor.release(postprocessor_request)

        start_time_comp = string_to_timestamp(job["final_start"])
        end_time_comp = string_to_timestamp(job["final_end"])
        deadline_comp = string_to_timestamp(job["deadline"])

        if start_time_comp < release_time:
            print("Error in start time calculation")
            return

        if start_time_comp > release_time:
            job["jobStartDelay"] = (start_time_comp - release_time).total_seconds()
            job_start_delays.append(job["jobStartDelay"])
        else:
            job["jobStartDelay"] = 0
        
        if end_time_comp > deadline_comp:
            job["jobEndDelay"] = (end_time_comp - deadline_comp).total_seconds()
            deadlin_exceeded.append(job["jobEndDelay"])
        else:
            job["jobEndDelay"] = 0

        job["order_release"] = job["order_release"].strftime('%Y-%m-%d %H:%M:%S')
        # job["setuptime_material"] = job["setuptime_material"].total_seconds()
        # job["setuptime_coil"] = job["setuptime_coil"].total_seconds()
        # job["duration_machine"] = job["duration_machine"].total_seconds()
        # job["duration_manual"] = job["duration_manual"].total_seconds()
        job["deadline"] = job["deadline"].strftime('%Y-%m-%d %H:%M:%S')
        job["latest_start"] = job["latest_start"].strftime('%Y-%m-%d %H:%M:%S')
        # job["setup_time"] = job["setup_time"].total_seconds()
        # job["status"] = job["status"].value
        
        scheduled_jobs.append(job)
        scheduled_jobs_in_cur_iter.append(job)

    def schedule_job(self, joblist):
        for job in joblist:
            self.env.process(self.run_job(job))   

class ProductionPlant:
    def __init__(self):
        self.manufacturing_layers = []
    
    def add_manufacturing_layer(self, manufacturing_layer):
        self.manufacturing_layers.append(manufacturing_layer)    

# Makespan = End time of last job - (Start time of first job - Setup time)
def get_makespan(job_list):
    min_start = None
    max_end = None
    for job in job_list:
        if not pd.isna(job["final_start"]):
            if not min_start or string_to_timestamp(job["final_start"]) < min_start:
                min_start = string_to_timestamp(job["final_start"]) - job["setuptime_material"] - job["setuptime_coil"]
                print(min_start, string_to_timestamp(job["final_start"]), job["setuptime_material"], job["setuptime_coil"])
            if not max_end or string_to_timestamp(job["final_end"]) > max_end:
                max_end = string_to_timestamp(job["final_end"])
    if min_start != None and max_end != None:
        return (max_end - min_start).total_seconds()
    else:
        delete_all_elements(max_machine_duration_flag)
        max_machine_duration_flag.append(True)

def delete_all_elements(my_list):
    for i in range(len(my_list) - 1, -1, -1):
        del my_list[i]
    return my_list

def get_desired_start(job_list):
    desired_start_date = None
    for job in job_list:
        setuptime_material = job["setuptime_material"]
        setuptime_coil = job["setuptime_coil"]
        job_duration = job['duration_machine']
        latest_start_time = job['deadline'] - job_duration - setuptime_material - setuptime_coil
        job['latest_start'] = latest_start_time

        if desired_start_date == None:
            desired_start_date = latest_start_time
        if latest_start_time < desired_start_date:
            desired_start_date = latest_start_time
        
        # if string_to_timestamp(job['deadline']).timestamp() < string_to_timestamp(desired_start_date.strftime('%Y-%m-%d %H:%M:%S')).timestamp() + max_machine_duration[0]:
        #     print("Before",job['job'] , string_to_timestamp(job['deadline']).timestamp() , string_to_timestamp(desired_start_date.strftime('%Y-%m-%d %H:%M:%S')).timestamp() , max_machine_duration[0])
        #     delete_all_elements(max_machine_duration)
        #     new_max_machine_duration = string_to_timestamp(job['deadline']).timestamp() - string_to_timestamp(desired_start_date.strftime('%Y-%m-%d %H:%M:%S')).timestamp()
        #     max_machine_duration.append(new_max_machine_duration)
        #     delete_all_elements(max_machine_duration_flag)
        #     max_machine_duration_flag.append(False)
        #     print("After",job['job'] , string_to_timestamp(job['deadline']).timestamp() , string_to_timestamp(desired_start_date.strftime('%Y-%m-%d %H:%M:%S')).timestamp() , max_machine_duration[0])
        #     print("Something needs to be done here")

    return desired_start_date.strftime('%Y-%m-%d %H:%M:%S')

def final_end_max(scheduled_jobs):
    max_timestamp = 0
    if scheduled_jobs != []:
        for item in scheduled_jobs:
            if string_to_timestamp(item["final_end"]).timestamp() > max_timestamp:
                max_timestamp = string_to_timestamp(item["final_end"]).timestamp()

    return max_timestamp

def convert_list_to_json(input_list):
    output_list = []
    for job in input_list:
        output_dict = {}
        for key, value in job.items():
            if value is None:  # Check for null values
                output_dict[key] = None
            elif key in ['job', 'selected_machine']:
                output_dict[key] = int(value)
            elif key in ['start', 'end', 'latest_start', 'calculated_start', 'calculated_end', 'planned_start', 'planned_end', 'final_start', 'final_end']:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                output_dict[key] = Timestamp(value.strftime('%Y-%m-%d %H:%M:%S'))
            elif key in ['setuptime_material', 'setuptime_coil', 'duration_machine', 'duration_manual', 'setup_time']:
                output_dict[key] = Timedelta(value)
            # elif key == 'status':
            #     output_dict[key] = JobStatus[value]
            else:
                output_dict[key] = value
        output_dict['order_release'] = output_dict.pop('start')
        output_dict['deadline'] = output_dict.pop('end')
        output_list.append(output_dict)
    return output_list

def simulate_and_schedule(ids, input_jobs):
    if isinstance(input_jobs, list) and all(isinstance(job, collections.OrderedDict) for job in input_jobs):
        input_jobs = convert_list_to_json(input_jobs)

    total_job_start_delays = []
    total_deadlin_exceeded = []
    makespans = []
    delete_all_elements(max_machine_duration)
    max_machine_duration.append(max_machine_duration_default)
    starttime = time.time()
    print("Simpy Simulation Start")
    df = pd.DataFrame(input_jobs)
    df = df.reindex(ids)
    job_list = df.to_dict(orient='records')
    ml1 = ManufacturingLayer()

    pp = ProductionPlant()
    pp.add_manufacturing_layer(ml1)
    for i, manufacturing_layer in enumerate(pp.manufacturing_layers):
        while len(scheduled_jobs) < len(job_list):
            jobs_not_scheduled = [job for job in job_list if job not in scheduled_jobs]
            desired_start_date = get_desired_start(jobs_not_scheduled)
            if scheduled_jobs == []: # give 11.6 days buffer for 1st batch jobs
                desired_start_date = string_to_timestamp(desired_start_date).timestamp() - df['duration_machine'].max().total_seconds()
            if scheduled_jobs != []: # no buffer for the next batch jobs
                end_max = final_end_max(scheduled_jobs)
                # print(desired_start_date, end_max)
                desired_start_date = max(string_to_timestamp(desired_start_date).timestamp(), end_max)
                print(f"final_end_max time for the scheduled batch of jobs: {datetime.fromtimestamp(end_max)}")
            print(f"Desired start time for the batch of jobs: {datetime.fromtimestamp(desired_start_date)}")

            env = simpy.Environment(initial_time = desired_start_date)
            m1531 = Machine(env, "1531")
            m1532 = Machine(env, "1532")
            m1533 = Machine(env, "1533")
            m1534 = Machine(env, "1534")
            m1535 = Machine(env, "1535")
            m1536 = Machine(env, "1536")
            m1537 = Machine(env, "1537")
            m1541 = Machine(env, "1541")
            m1542 = Machine(env, "1542")
            m1543 = Machine(env, "1543")
            operator1 = Operator(env, "operator1")
            operator2 = Operator(env, "operator2")
            operator3 = Operator(env, "operator3")
            postprocessor1 = Postprocessor(env, "postprocessor1")
            postprocessor2 = Postprocessor(env, "postprocessor2")
            postprocessor3 = Postprocessor(env, "postprocessor3")
            postprocessor4 = Postprocessor(env, "postprocessor4")

            mg1 = MachineGroup(env, "group1")
            mg1.add_machine(m1537)
            mg1.add_machine(m1536)
            mg1.add_machine(m1535)
            mg1.add_operator(operator1)
            mg1.add_postprocessor(postprocessor1)

            mg2 = MachineGroup(env, "group2")
            mg2.add_machine(m1534)
            mg2.add_machine(m1533)
            mg2.add_machine(m1532)
            mg2.add_operator(operator2)
            mg2.add_postprocessor(postprocessor2)

            mg3 = MachineGroup(env, "group3")
            mg3.add_machine(m1531)
            mg3.add_machine(m1541)
            mg3.add_machine(m1542)
            mg3.add_machine(m1543)
            mg3.add_operator(operator3)
            mg3.add_postprocessor(postprocessor3)
            # mg3.add_postprocessor(postprocessor4)

            ml1.add_machine_group(mg1)
            ml1.add_machine_group(mg2)
            ml1.add_machine_group(mg3)
            ml1.env = env

            manufacturing_layer.schedule_job(jobs_not_scheduled)
            env.run()

            makespan = get_makespan(scheduled_jobs_in_cur_iter)
            print("Makespan: ", makespan)
            if makespan != None:
                makespans_cur_iter.append(makespan)

            delete_all_elements(scheduled_jobs_in_cur_iter)
            ml1.machine_groups = []
            # print(max_machine_duration)
            if max_machine_duration[0] < df['duration_machine'].max().total_seconds():
                delete_all_elements(max_machine_duration)
                max_machine_duration.append(df['duration_machine'].max().total_seconds())

        print("Deadline exceeded for these many jobs: ", len(deadlin_exceeded))
        print("Sum of deadline delays: ", sum(deadlin_exceeded))
        # print("Start delay for these many jobs: ", len(job_start_delays))
        # print("Sum of job start delays: ", sum(job_start_delays))
        makespans.append(str(makespans_cur_iter))
        total_job_start_delays.append(sum(job_start_delays))
        total_deadlin_exceeded.append(sum(deadlin_exceeded))
        delete_all_elements(job_start_delays)
        delete_all_elements(deadlin_exceeded)
        print("Total makespan: ", sum(makespans_cur_iter))
        delete_all_elements(scheduled_jobs)
        delete_all_elements(makespans_cur_iter)

    endtime = time.time()
    print("Simpy Simulation End")
    print("Simpy Simulation Time: ",endtime - starttime)
    # print(job_list)

    # Replace NaT with empty strings
    for item in job_list:
        for key, value in item.items():
            if isinstance(value, str):
                continue
            elif pd.isna(value):
                item[key] = ""
            elif key in ['start', 'end', 'latest_start', 'calculated_start', 'calculated_end', 'planned_start', 'planned_end', 'final_start', 'final_end']:
                value = pd.to_datetime(value)
        item.update({'start': item.pop('order_release')})
        item.update({'end': item.pop('deadline')})

    with open('data.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(job_list[0].keys())
        for item in job_list:
            writer.writerow(item.values())

    return makespans, total_deadlin_exceeded, job_list

if __name__ == "__main__":
    df_init = orders.get_westaflex_orders()

    sorting_tech = "deadline"
    # baseline approaches, presorts the joblist
    if sorting_tech == "SJF":
        df = df_init.sort_values(by='duration_machine')
        ids = list(df.index)
    elif sorting_tech == "LJF":
        df = df_init.sort_values(by='duration_machine', ascending=False)
        ids = list(df.index)
    elif sorting_tech == "deadline":
        df = df_init.sort_values(by='deadline')
        ids = list(df.index)
    elif sorting_tech == "releasedate":
        df = df_init.sort_values(by='order_release')
        ids = list(df.index)
    elif sorting_tech == "random":
        ids = df_init.sample(frac=1, random_state=42).index.to_list()

    job_list = df_init.to_dict(orient='records')

    makespans, total_deadlin_exceeded, job_list = simulate_and_schedule(ids=ids, input_jobs=job_list)
    print(makespans, total_deadlin_exceeded)
