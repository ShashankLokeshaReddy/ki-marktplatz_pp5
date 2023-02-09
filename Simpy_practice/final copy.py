import simpy
import random
from datetime import datetime
import pandas as pd

def string_to_timestamp(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S")

class Machine:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.machine = simpy.Resource(env, capacity=1)
    
    def is_available(self, job):
        # return self.machine.capacity > 0
        if self.machine.count == 0:
            availability = True
        else:
            availability = False
        return availability
    
    # def run_job(self, job):
    #     release_time = string_to_timestamp(job["jobInputDate"])
    #     current_time = datetime.fromtimestamp(self.env.now)
    #     diff_delay = max((release_time - current_time).total_seconds(),0)
    #     yield self.env.timeout(diff_delay)
    #     with self.machine.request() as req:
    #         yield req
    #         self.availability = False
    #         print("self.availability = False",self.availability)

    #         start = self.env.now
    #         job["productionStart"] = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
    #         job["resourceId"] = self.name
    #         print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} starts at {job['productionStart']}")
    #         yield self.env.timeout(job["productionDuration"] * 60) # minutes to seconds
    #         job["productionEnd"] = datetime.fromtimestamp(self.env.now).strftime("%Y-%m-%d %H:%M:%S")
    #         print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} ends at {job['productionEnd']}")

    #         start_time_comp = datetime.strptime(job["productionStart"], "%Y-%m-%d %H:%M:%S")
    #         release_date_comp = datetime.strptime(job["jobInputDate"], "%Y-%m-%d %H:%M:%S")
    #         end_time_comp = datetime.strptime(job["productionEnd"], "%Y-%m-%d %H:%M:%S")
    #         deadline_comp = datetime.strptime(job["deadlineDate"], "%Y-%m-%d %H:%M:%S")
    #         self.availability = True
    #         print("self.availability = True",self.availability)

    #         if start_time_comp > release_date_comp:
    #             job["jobStartDelay"] = (start_time_comp - release_date_comp).total_seconds()
    #             job_start_delays.append(job["jobStartDelay"])
            
    #         if end_time_comp > deadline_comp:
    #             job["jobEndDelay"] = (end_time_comp - deadline_comp).total_seconds()
    #             deadlin_exceeded.append(job["jobEndDelay"])

    def run_job(self, job):
        release_time = string_to_timestamp(job["jobInputDate"])
        current_time = datetime.fromtimestamp(self.env.now)
        diff_delay = max((release_time - current_time).total_seconds(),0)
        yield self.env.timeout(diff_delay)

        machine_request = self.machine.request()
        yield machine_request
        print(self.name," self.availability = False :",self.machine.capacity, self.machine.count)

        start = self.env.now
        job["productionStart"] = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
        job["resourceId"] = self.name
        print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} starts at {job['productionStart']}")
        yield self.env.timeout(job["productionDuration"] * 60) # minutes to seconds
        job["productionEnd"] = datetime.fromtimestamp(self.env.now).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} ends at {job['productionEnd']}")
        self.machine.release(machine_request)
        print(job['resourceId']," self.availability = False :",self.machine.capacity, self.machine.count)

        start_time_comp = datetime.strptime(job["productionStart"], "%Y-%m-%d %H:%M:%S")
        release_date_comp = datetime.strptime(job["jobInputDate"], "%Y-%m-%d %H:%M:%S")
        end_time_comp = datetime.strptime(job["productionEnd"], "%Y-%m-%d %H:%M:%S")
        deadline_comp = datetime.strptime(job["deadlineDate"], "%Y-%m-%d %H:%M:%S")
        
        if start_time_comp > release_date_comp:
            job["jobStartDelay"] = (start_time_comp - release_date_comp).total_seconds()
            job_start_delays.append(job["jobStartDelay"])
        
        if end_time_comp > deadline_comp:
            job["jobEndDelay"] = (end_time_comp - deadline_comp).total_seconds()
            deadlin_exceeded.append(job["jobEndDelay"])

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
                available_machines.append(machine)
        return available_machines 

    def schedule_job(self, job):
        available_machines = self.get_available_machines(self.machines, job) #[machine for machine in self.machines if machine.is_available(job)]
        print("available_machines:",len(available_machines))
        if available_machines:
            chosen_machine = random.choice(available_machines)
            self.env.process(chosen_machine.run_job(job))

class ManufacturingLayer:
    def __init__(self, env):
        self.env = env
        self.machine_groups = []
    
    def add_machine_group(self, machine_group):
        self.machine_groups.append(machine_group)
    
    def schedule_job(self, job):
        for machine_group in self.machine_groups:
            if machine_group.group_name == job["group"]:
                machine_group.schedule_job(job)
                break

class ProductionPlant:
    def __init__(self, env):
        self.env = env
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

def parse_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

# def schedule_jobs(env, layer, job_list):
#     print("Schedule")
#     for job in job_list:
#         # yield env.timeout((parse_datetime(job["jobInputDate"]) - env.now).total_seconds())
#         layer.schedule_job(job)


job_start_delays = []
deadlin_exceeded = []

def main():
    env = simpy.Environment()

    m0 = Machine(env, "M0")
    m1 = Machine(env, "M1")
    m2 = Machine(env, "M2")
    m3 = Machine(env, "M3")
    m4 = Machine(env, "M4")
    m5 = Machine(env, "M5")
    m6 = Machine(env, "M6")
    m7 = Machine(env, "M7")
    m8 = Machine(env, "M8")
    m9 = Machine(env, "M9")

    # op0 = Operator(env, "Op0")
    # op1 = Operator(env, "Op1")
    # op2 = Operator(env, "Op2")
    # op3 = Operator(env, "Op3")

    mg1 = MachineGroup(env, "group1")
    mg1.add_machine(m0)
    mg1.add_machine(m1)
    mg1.add_machine(m2)
    # mg1.add_operator(op0)
    # mg1.add_operator(op1)

    mg1.add_machine(m3)
    mg1.add_machine(m4)
    mg1.add_machine(m5)
    # mg2.add_operator(op2)
    # mg2.add_operator(op3)


    mg1.add_machine(m6)
    mg1.add_machine(m7)
    mg1.add_machine(m8)
    mg1.add_machine(m9)
    # mg2.add_operator(op2)
    # mg2.add_operator(op3)

    ml1 = ManufacturingLayer(env)
    ml1.add_machine_group(mg1)
    # ml1.add_machine_group(mg2)
    # ml1.add_machine_group(mg3)

    # ml2 = ManufacturingLayer(env)
    # ml2.add_machine_group(mg1)
    # ml2.add_machine_group(mg2)

    # mp = ManufacturingLayer(env)
    # mp.add_machine_group(ml1)
    # mp.add_machine_group(ml2)
    pp = ProductionPlant(env)
    pp.add_manufacturing_layer(ml1)

    if True:
        print("Groups in ml1: ")
        for mg in ml1.machine_groups:
            print(mg.group_name)
        print("Machines in mg1: ")
        for mc in mg1.machines:
            print(mc.name)
        print("Machines in mg2: ")
        # for mc in mg2.machines:
        #     print(mc.name)

    job_list = [
        {
        "id": 0,
        "jobID": 0,
        "partID": "P0",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 323.96,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 1,
        "jobID": 1,
        "partID": "P1",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-02 08:54:00",
        "productionDuration": 147.19,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 2,
        "jobID": 2,
        "partID": "P2",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-02 08:54:00",
        "productionDuration": 124.49,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 3,
        "jobID": 3,
        "partID": "P3",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-02 08:54:00",
        "productionDuration": 104.03,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 4,
        "jobID": 4,
        "partID": "P4",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 08:54:00",
        "productionDuration": 570.94,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 5,
        "jobID": 5,
        "partID": "P5",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 08:54:00",
        "productionDuration": 75.24,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 6,
        "jobID": 6,
        "partID": "P6",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 08:54:00",
        "productionDuration": 53.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 7,
        "jobID": 7,
        "partID": "P7",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 42.59,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 8,
        "jobID": 8,
        "partID": "P8",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 19.68,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 9,
        "jobID": 9,
        "partID": "P9",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 19.9,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 10,
        "jobID": 10,
        "partID": "P10",
        "resourceId": "", 
        "group": "group1",
        "jobInputDate": "2021-09-01 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 19.55,
        "productionStart": "",
        "productionEnd": ""
        }
    ]

    sorting_tech = ""
    # baseline approaches, presorts the joblist
    if sorting_tech == "SJF":
        job_list = sorted(job_list, key=lambda x: x['productionDuration'])
    elif sorting_tech == "LJF":
        job_list = sorted(job_list, key=lambda x: x['productionDuration'], reverse=True)
    elif sorting_tech == "deadline":
        job_list = sorted(job_list, key=lambda x: datetime.strptime(x['deadlineDate'], '%Y-%m-%d %H:%M:%S'))
    elif sorting_tech == "releasedate":
        job_list = sorted(job_list, key=lambda x: datetime.strptime(x['jobInputDate'], '%Y-%m-%d %H:%M:%S'))
    elif sorting_tech == "random":
        random.shuffle(job_list)
        job_list = job_list
    output = pp.schedule_jobs(job_list)
    
    env.run()
    print(output)
    print("Deadline exceeded for these many jobs: ", len(deadlin_exceeded))
    print("These are the job IDs of those jobs: ", sum(deadlin_exceeded))
    print("Start delay for these many jobs: ", len(job_start_delays))
    print("job_start_delays: ", sum(job_start_delays))

if __name__ == "__main__":
    main()
