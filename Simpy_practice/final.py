import simpy
import random
from datetime import datetime
import pandas as pd
import pendulum

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

    def run_job(self, job):
        # for job in sublist:
        release_time = string_to_timestamp(job["jobInputDate"])
        current_time = datetime.fromtimestamp(self.env.now)
        diff_delay = max((release_time - current_time).total_seconds(),0)
        yield self.env.timeout(diff_delay)

        available_machines = self.get_available_machines(self.machines, job)
        while not available_machines:
            yield self.env.timeout(1)
            available_machines = [machine for machine in self.machines if machine.is_available(job)]
         
        chosen_machine = random.choice(available_machines)
        machine_request = chosen_machine.machine.request()
        yield machine_request
        print(chosen_machine.name," self.availability = False :",chosen_machine.machine.capacity, chosen_machine.machine.count)

        start = self.env.now
        job["productionStart"] = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
        job["resourceId"] = chosen_machine.name
        print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} starts at {job['productionStart']}")
        yield self.env.timeout(job["productionDuration"] * 60) # minutes to seconds
        job["productionEnd"] = datetime.fromtimestamp(self.env.now).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} ends at {job['productionEnd']}")
        chosen_machine.machine.release(machine_request)
        print(job['resourceId']," self.availability = False :",chosen_machine.machine.capacity, chosen_machine.machine.count)

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

    def schedule_job(self, sublist):
        for job in sublist:
            self.env.process(self.run_job(job))          

class ManufacturingLayer:
    def __init__(self, env):
        self.env = env
        self.machine_groups = []
    
    def add_machine_group(self, machine_group):
        self.machine_groups.append(machine_group)
    
    def schedule_job(self, joblist):
        group_dict = {}
        for job in joblist:
            group = job['group']
            if group in group_dict:
                group_dict[group].append(job)
            else:
                group_dict[group] = [job]

        for machine_group in self.machine_groups:
            for group, sublist in group_dict.items():
                if machine_group.group_name ==group:
                    print(f"Group: {group}")
                    print(f"Sublist: {sublist}")
                    machine_group.schedule_job(sublist)
                    # break

class ProductionPlant:
    def __init__(self, env):
        self.env = env
        self.manufacturing_layers = []
    
    def add_manufacturing_layer(self, manufacturing_layer):
        self.manufacturing_layers.append(manufacturing_layer)
    
    def schedule_jobs(self, joblist):
        job_queues = [joblist]
        for i, manufacturing_layer in enumerate(self.manufacturing_layers):
            manufacturing_layer.schedule_job(joblist)


def parse_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

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

    mg2 = MachineGroup(env, "group2")
    mg2.add_machine(m3)
    mg2.add_machine(m4)
    mg2.add_machine(m5)
    # mg2.add_operator(op2)
    # mg2.add_operator(op3)

    mg3 = MachineGroup(env, "group3")
    mg3.add_machine(m6)
    mg3.add_machine(m7)
    mg3.add_machine(m8)
    mg3.add_machine(m9)
    # mg2.add_operator(op2)
    # mg2.add_operator(op3)

    ml1 = ManufacturingLayer(env)
    ml1.add_machine_group(mg1)
    ml1.add_machine_group(mg2)
    ml1.add_machine_group(mg3)

    # ml2 = ManufacturingLayer(env)
    # ml2.add_machine_group(mg1)
    # ml2.add_machine_group(mg2)

    # mp = ManufacturingLayer(env)
    # mp.add_machine_group(ml1)
    # mp.add_machine_group(ml2)
    pp = ProductionPlant(env)
    pp.add_manufacturing_layer(ml1)

    job_list = [
        {
        "id": 0,
        "jobID": 0,
        "partID": "P0",
        "resourceId": "", 
        "group" : "group1",
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
        "group" : "group1",
        "jobInputDate": "2021-09-02 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-03 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-04 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-05 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-06 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-07 00:00:00",
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
        "group" : "group2",
        "jobInputDate": "2021-09-08 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-09 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-10 00:00:00",
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
        "group" : "group1",
        "jobInputDate": "2021-09-11 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 19.55,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 11,
        "jobID": 11,
        "partID": "P11",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-12 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 17.98,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 12,
        "jobID": 12,
        "partID": "P12",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-09-13 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 15.66,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 13,
        "jobID": 13,
        "partID": "P13",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-14 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 273.46,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 14,
        "jobID": 14,
        "partID": "P14",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-15 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 55.77,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 15,
        "jobID": 15,
        "partID": "P15",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-16 00:00:00",
        "deadlineDate": "2022-05-06 03:09:00",
        "productionDuration": 38.26,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 16,
        "jobID": 16,
        "partID": "P16",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-17 00:00:00",
        "deadlineDate": "2022-05-06 03:09:00",
        "productionDuration": 36.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 17,
        "jobID": 17,
        "partID": "P17",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-18 00:00:00",
        "deadlineDate": "2022-05-06 03:09:00",
        "productionDuration": 49.78,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 18,
        "jobID": 18,
        "partID": "P18",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-19 00:00:00",
        "deadlineDate": "2022-05-06 09:09:00",
        "productionDuration": 79.87,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 19,
        "jobID": 19,
        "partID": "P19",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-20 00:00:00",
        "deadlineDate": "2022-05-06 09:09:00",
        "productionDuration": 206.55,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 20,
        "jobID": 20,
        "partID": "P20",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-21 00:00:00",
        "deadlineDate": "2022-05-06 09:09:00",
        "productionDuration": 15.2,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 21,
        "jobID": 21,
        "partID": "P21",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-22 00:00:00",
        "deadlineDate": "2022-05-10 08:54:00",
        "productionDuration": 300.61,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 22,
        "jobID": 22,
        "partID": "P22",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-23 00:00:00",
        "deadlineDate": "2022-05-10 08:54:00",
        "productionDuration": 34.39,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 23,
        "jobID": 23,
        "partID": "P23",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-24 00:00:00",
        "deadlineDate": "2022-05-05 20:49:00",
        "productionDuration": 16,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 24,
        "jobID": 24,
        "partID": "P21",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-09-25 00:00:00",
        "deadlineDate": "2022-05-10 08:54:00",
        "productionDuration": 243.21,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 25,
        "jobID": 25,
        "partID": "P24",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-26 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 156.16,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 26,
        "jobID": 26,
        "partID": "P14",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-27 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 34.39,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 27,
        "jobID": 27,
        "partID": "P25",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-28 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 170.01,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 28,
        "jobID": 28,
        "partID": "P26",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-29 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 36.03,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 29,
        "jobID": 29,
        "partID": "P27",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-09-30 00:00:00",
        "deadlineDate": "2022-05-16 08:54:00",
        "productionDuration": 19.05,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 30,
        "jobID": 30,
        "partID": "P19",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-01 00:00:00",
        "deadlineDate": "2022-05-16 08:54:00",
        "productionDuration": 206.55,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 31,
        "jobID": 31,
        "partID": "P28",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-02 00:00:00",
        "deadlineDate": "2022-05-16 08:54:00",
        "productionDuration": 16.81,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 32,
        "jobID": 32,
        "partID": "P1",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-03 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 203.27,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 33,
        "jobID": 33,
        "partID": "P29",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-04 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 92.85,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 34,
        "jobID": 34,
        "partID": "P30",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-05 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 55.77,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 35,
        "jobID": 35,
        "partID": "P31",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-06 00:00:00",
        "deadlineDate": "2022-05-06 09:09:00",
        "productionDuration": 306.58,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 36,
        "jobID": 36,
        "partID": "P32",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-07 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 306.58,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 37,
        "jobID": 37,
        "partID": "P33",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-08 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 52.02,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 38,
        "jobID": 38,
        "partID": "P34",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-09 00:00:00",
        "deadlineDate": "2022-05-13 03:09:00",
        "productionDuration": 31.73,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 39,
        "jobID": 39,
        "partID": "P35",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-10 00:00:00",
        "deadlineDate": "2022-05-16 08:54:00",
        "productionDuration": 31.12,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 40,
        "jobID": 40,
        "partID": "P36",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-11 00:00:00",
        "deadlineDate": "2022-05-10 08:54:00",
        "productionDuration": 121.28,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 41,
        "jobID": 41,
        "partID": "P37",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-12 00:00:00",
        "deadlineDate": "2022-05-10 08:54:00",
        "productionDuration": 126.94,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 42,
        "jobID": 42,
        "partID": "P38",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-13 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 40.79,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 43,
        "jobID": 43,
        "partID": "P39",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-14 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 16.43,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 44,
        "jobID": 44,
        "partID": "P40",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-15 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 190.9,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 45,
        "jobID": 45,
        "partID": "P41",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-16 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 16.48,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 46,
        "jobID": 46,
        "partID": "P42",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-17 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 357.73,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 47,
        "jobID": 47,
        "partID": "P43",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-10-18 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 1669.83,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 48,
        "jobID": 48,
        "partID": "P44",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-19 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 62.85,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 49,
        "jobID": 49,
        "partID": "P45",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-20 00:00:00",
        "deadlineDate": "2022-05-16 08:54:00",
        "productionDuration": 41.33,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 50,
        "jobID": 50,
        "partID": "P1",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-21 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 203.27,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 51,
        "jobID": 51,
        "partID": "P29",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-22 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 92.85,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 52,
        "jobID": 52,
        "partID": "P46",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-23 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 15.2,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 53,
        "jobID": 53,
        "partID": "P47",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-24 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 15.18,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 54,
        "jobID": 54,
        "partID": "P0",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-10-25 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 223.96,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 55,
        "jobID": 55,
        "partID": "P48",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-26 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 181.27,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 56,
        "jobID": 56,
        "partID": "P14",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-27 00:00:00",
        "deadlineDate": "2022-05-20 03:09:00",
        "productionDuration": 90.91,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 57,
        "jobID": 57,
        "partID": "P49",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-28 00:00:00",
        "deadlineDate": "2022-05-20 03:09:00",
        "productionDuration": 63.53,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 58,
        "jobID": 58,
        "partID": "P50",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-29 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 15.72,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 59,
        "jobID": 59,
        "partID": "P13",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-30 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 207.35,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 60,
        "jobID": 60,
        "partID": "P22",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-10-31 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 55.77,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 61,
        "jobID": 61,
        "partID": "P51",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-01 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 51.66,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 62,
        "jobID": 62,
        "partID": "P52",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-02 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 19.9,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 63,
        "jobID": 63,
        "partID": "P20",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-03 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 15.19,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 64,
        "jobID": 64,
        "partID": "P53",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-04 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 15.03,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 65,
        "jobID": 65,
        "partID": "P54",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-05 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 16.31,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 66,
        "jobID": 66,
        "partID": "P25",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-06 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 198.59,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 67,
        "jobID": 67,
        "partID": "P22",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-07 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 55.77,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 68,
        "jobID": 68,
        "partID": "P34",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-08 00:00:00",
        "deadlineDate": "2022-05-20 03:09:00",
        "productionDuration": 87.91,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 69,
        "jobID": 69,
        "partID": "P55",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-09 00:00:00",
        "deadlineDate": "2022-05-20 03:09:00",
        "productionDuration": 55.14,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 70,
        "jobID": 70,
        "partID": "P56",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-10 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 15.82,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 71,
        "jobID": 71,
        "partID": "P57",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-11 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 15.73,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 72,
        "jobID": 72,
        "partID": "P58",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-12 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 199.12,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 73,
        "jobID": 73,
        "partID": "P43",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-13 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 1911.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 74,
        "jobID": 74,
        "partID": "P42",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-14 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 125.24,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 75,
        "jobID": 75,
        "partID": "P59",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-15 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 35.01,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 76,
        "jobID": 76,
        "partID": "P42",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-16 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 1167.43,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 77,
        "jobID": 77,
        "partID": "P60",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-17 00:00:00",
        "deadlineDate": "2022-05-20 03:09:00",
        "productionDuration": 117,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 78,
        "jobID": 78,
        "partID": "P61",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-18 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 16.11,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 79,
        "jobID": 79,
        "partID": "P62",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-19 00:00:00",
        "deadlineDate": "2022-05-20 09:09:00",
        "productionDuration": 49.45,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 80,
        "jobID": 80,
        "partID": "P63",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-20 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 16.26,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 81,
        "jobID": 81,
        "partID": "P64",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-21 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 76.48,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 82,
        "jobID": 82,
        "partID": "P65",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-22 00:00:00",
        "deadlineDate": "2022-05-16 08:54:00",
        "productionDuration": 1088.97,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 83,
        "jobID": 83,
        "partID": "P66",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-23 00:00:00",
        "deadlineDate": "2022-05-17 08:54:00",
        "productionDuration": 840.33,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 84,
        "jobID": 84,
        "partID": "P67",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-24 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 383.7,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 85,
        "jobID": 85,
        "partID": "P68",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-25 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 136.59,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 86,
        "jobID": 86,
        "partID": "P69",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-26 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 118.15,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 87,
        "jobID": 87,
        "partID": "P70",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-27 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 139.07,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 88,
        "jobID": 88,
        "partID": "P71",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-11-28 00:00:00",
        "deadlineDate": "2022-05-19 20:49:00",
        "productionDuration": 94.01,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 89,
        "jobID": 89,
        "partID": "P25",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-29 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 192.56,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 90,
        "jobID": 90,
        "partID": "P22",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-11-30 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 55.77,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 91,
        "jobID": 91,
        "partID": "P2",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-01 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 38.87,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 92,
        "jobID": 92,
        "partID": "P72",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-02 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 17.09,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 93,
        "jobID": 93,
        "partID": "P29",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-03 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 92.85,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 94,
        "jobID": 94,
        "partID": "P73",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-04 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 36.57,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 95,
        "jobID": 95,
        "partID": "P74",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-05 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 25.62,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 96,
        "jobID": 96,
        "partID": "P75",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-06 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 50.89,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 97,
        "jobID": 97,
        "partID": "P26",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-07 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 183.49,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 98,
        "jobID": 98,
        "partID": "P13",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-08 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 109.17,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 99,
        "jobID": 99,
        "partID": "P14",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-09 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 34.39,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 100,
        "jobID": 100,
        "partID": "P17",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-10 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 29.75,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 101,
        "jobID": 101,
        "partID": "P76",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-11 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 38.1,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 102,
        "jobID": 102,
        "partID": "P77",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-12 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 31.22,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 103,
        "jobID": 103,
        "partID": "P78",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-13 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 201.41,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 104,
        "jobID": 104,
        "partID": "P79",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-14 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 198.71,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 105,
        "jobID": 105,
        "partID": "P80",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-15 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 184.35,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 106,
        "jobID": 106,
        "partID": "P81",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-16 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 117.95,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 107,
        "jobID": 107,
        "partID": "P2",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-17 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 86.66,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 108,
        "jobID": 108,
        "partID": "P5",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-18 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 110.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 109,
        "jobID": 109,
        "partID": "P82",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-19 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 51.04,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 110,
        "jobID": 110,
        "partID": "P83",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-20 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 15.35,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 111,
        "jobID": 111,
        "partID": "P84",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-12-21 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 106.87,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 112,
        "jobID": 112,
        "partID": "P31",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-22 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 1923.63,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 113,
        "jobID": 113,
        "partID": "P34",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-23 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 31.73,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 114,
        "jobID": 114,
        "partID": "P85",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-24 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 50.54,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 115,
        "jobID": 115,
        "partID": "P86",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2021-12-25 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 18.22,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 116,
        "jobID": 116,
        "partID": "P87",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-12-26 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 62.97,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 117,
        "jobID": 117,
        "partID": "P44",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-12-27 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 49.38,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 118,
        "jobID": 118,
        "partID": "P88",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2021-12-28 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 47.75,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 119,
        "jobID": 119,
        "partID": "P89",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-29 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 19.83,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 120,
        "jobID": 120,
        "partID": "P90",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-30 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 21.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 121,
        "jobID": 121,
        "partID": "P38",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2021-12-31 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 20.02,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 122,
        "jobID": 122,
        "partID": "P65",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-01 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 909.31,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 123,
        "jobID": 123,
        "partID": "P68",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-02 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 136.59,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 124,
        "jobID": 124,
        "partID": "P65",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-03 00:00:00",
        "deadlineDate": "2022-05-30 08:54:00",
        "productionDuration": 1088.97,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 125,
        "jobID": 125,
        "partID": "P91",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-04 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 2572.09,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 126,
        "jobID": 126,
        "partID": "P92",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-05 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 124.61,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 127,
        "jobID": 127,
        "partID": "P93",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-06 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 606.03,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 128,
        "jobID": 128,
        "partID": "P94",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-07 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 15.72,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 129,
        "jobID": 129,
        "partID": "P95",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-08 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 1879.07,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 130,
        "jobID": 130,
        "partID": "P96",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-09 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 2366.81,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 131,
        "jobID": 131,
        "partID": "P97",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-10 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 8945.19,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 132,
        "jobID": 132,
        "partID": "P98",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-11 00:00:00",
        "deadlineDate": "2022-05-12 20:49:00",
        "productionDuration": 8440.2,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 133,
        "jobID": 133,
        "partID": "P99",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-12 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 1535.47,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 134,
        "jobID": 134,
        "partID": "P99",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-13 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 1643.36,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 135,
        "jobID": 135,
        "partID": "P99",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-14 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 1643.36,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 136,
        "jobID": 136,
        "partID": "P99",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-15 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 1643.36,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 137,
        "jobID": 137,
        "partID": "P99",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-16 00:00:00",
        "deadlineDate": "2022-05-23 08:54:00",
        "productionDuration": 1643.36,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 138,
        "jobID": 138,
        "partID": "P100",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-17 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 568.69,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 139,
        "jobID": 139,
        "partID": "P100",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-18 00:00:00",
        "deadlineDate": "2022-05-25 02:54:00",
        "productionDuration": 568.69,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 140,
        "jobID": 140,
        "partID": "P101",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-19 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 533.69,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 141,
        "jobID": 141,
        "partID": "P102",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-20 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 368.47,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 142,
        "jobID": 142,
        "partID": "P103",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-21 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 506.18,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 143,
        "jobID": 143,
        "partID": "P104",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-22 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 484.12,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 144,
        "jobID": 144,
        "partID": "P101",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-23 00:00:00",
        "deadlineDate": "2022-05-13 09:09:00",
        "productionDuration": 533.69,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 145,
        "jobID": 145,
        "partID": "P105",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-24 00:00:00",
        "deadlineDate": "2022-05-24 08:54:00",
        "productionDuration": 318.53,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 146,
        "jobID": 146,
        "partID": "P106",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-25 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 254.44,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 147,
        "jobID": 147,
        "partID": "P107",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-26 00:00:00",
        "deadlineDate": "2022-05-24 20:49:00",
        "productionDuration": 67.34,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 148,
        "jobID": 148,
        "partID": "P78",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-27 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 201.39,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 149,
        "jobID": 149,
        "partID": "P79",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-01-28 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 196.68,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 150,
        "jobID": 150,
        "partID": "P80",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-29 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 184.35,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 151,
        "jobID": 151,
        "partID": "P81",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-01-30 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 175.14,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 152,
        "jobID": 152,
        "partID": "P2",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-01-31 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 86.66,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 153,
        "jobID": 153,
        "partID": "P5",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-02-01 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 110.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 154,
        "jobID": 154,
        "partID": "P7",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-02-02 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 59.2,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 155,
        "jobID": 155,
        "partID": "P108",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-03 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 15.47,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 156,
        "jobID": 156,
        "partID": "P109",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-04 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 46.84,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 157,
        "jobID": 157,
        "partID": "P110",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-05 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 15.51,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 158,
        "jobID": 158,
        "partID": "P111",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-06 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 15.3,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 159,
        "jobID": 159,
        "partID": "P112",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-07 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 15.19,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 160,
        "jobID": 160,
        "partID": "P30",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-08 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 305.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 161,
        "jobID": 161,
        "partID": "P13",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-09 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 173.29,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 162,
        "jobID": 162,
        "partID": "P113",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-10 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 106.6,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 163,
        "jobID": 163,
        "partID": "P114",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-11 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 71.73,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 164,
        "jobID": 164,
        "partID": "P115",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-12 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 48.35,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 165,
        "jobID": 165,
        "partID": "P116",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-13 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 17.61,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 166,
        "jobID": 166,
        "partID": "P117",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-14 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 28.12,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 167,
        "jobID": 167,
        "partID": "P118",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-15 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 25.49,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 168,
        "jobID": 168,
        "partID": "P119",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-16 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 18.22,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 169,
        "jobID": 169,
        "partID": "P120",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-02-17 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 15.55,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 170,
        "jobID": 170,
        "partID": "P121",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-18 00:00:00",
        "deadlineDate": "2022-06-03 15:09:00",
        "productionDuration": 31.22,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 171,
        "jobID": 171,
        "partID": "P22",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-19 00:00:00",
        "deadlineDate": "2022-06-03 15:09:00",
        "productionDuration": 114.24,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 172,
        "jobID": 172,
        "partID": "P122",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-20 00:00:00",
        "deadlineDate": "2022-06-03 15:09:00",
        "productionDuration": 26.8,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 173,
        "jobID": 173,
        "partID": "P3",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-21 00:00:00",
        "deadlineDate": "2022-06-07 08:54:00",
        "productionDuration": 100.75,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 174,
        "jobID": 174,
        "partID": "P123",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-22 00:00:00",
        "deadlineDate": "2022-06-07 08:54:00",
        "productionDuration": 96.32,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 175,
        "jobID": 175,
        "partID": "P33",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-02-23 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 128.06,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 176,
        "jobID": 176,
        "partID": "P36",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-02-24 00:00:00",
        "deadlineDate": "2022-05-31 08:54:00",
        "productionDuration": 69.15,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 177,
        "jobID": 177,
        "partID": "P37",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-02-25 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 634.67,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 178,
        "jobID": 178,
        "partID": "P40",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-26 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 554.12,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 179,
        "jobID": 179,
        "partID": "P124",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-02-27 00:00:00",
        "deadlineDate": "2022-06-02 20:49:00",
        "productionDuration": 157.15,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 180,
        "jobID": 180,
        "partID": "P125",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-02-28 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 15.18,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 181,
        "jobID": 181,
        "partID": "P43",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-03-01 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 1669.83,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 182,
        "jobID": 182,
        "partID": "P42",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-03-02 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 125.24,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 183,
        "jobID": 183,
        "partID": "P60",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-03-03 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 122.77,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 184,
        "jobID": 184,
        "partID": "P44",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-03-04 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 62.85,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 185,
        "jobID": 185,
        "partID": "P126",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-03-05 00:00:00",
        "deadlineDate": "2022-06-03 03:09:00",
        "productionDuration": 37.52,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 186,
        "jobID": 186,
        "partID": "P127",
        "resourceId": "", 
        "group" : "group1",
        "jobInputDate": "2022-03-06 00:00:00",
        "deadlineDate": "2022-06-03 15:09:00",
        "productionDuration": 157.74,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 187,
        "jobID": 187,
        "partID": "P62",
        "resourceId": "", 
        "group" : "group2",
        "jobInputDate": "2022-03-07 00:00:00",
        "deadlineDate": "2022-06-03 15:09:00",
        "productionDuration": 32.9,
        "productionStart": "",
        "productionEnd": ""
        },
        {
        "id": 188,
        "jobID": 188,
        "partID": "P38",
        "resourceId": "", 
        "group" : "group3",
        "jobInputDate": "2022-03-08 00:00:00",
        "deadlineDate": "2022-06-03 15:09:00",
        "productionDuration": 2720.18,
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
    print(job_list)
    print("Deadline exceeded for these many jobs: ", len(deadlin_exceeded))
    print("These are the job IDs of those jobs: ", sum(deadlin_exceeded))
    print("Start delay for these many jobs: ", len(job_start_delays))
    print("Sum of job start delays: ", sum(job_start_delays))

if __name__ == "__main__":
    main()
