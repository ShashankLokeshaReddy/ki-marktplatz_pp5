import simpy
import pendulum
from datetime import datetime
import random

# Helper function to convert string to timestamp
def string_to_timestamp(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S")

# Helper function to check if machine is available
def check_machine_availability(resourceId, env, machines):
    if resourceId in machines:
        return machines[resourceId].request()
    else:
        machines[resourceId] = simpy.Resource(env, capacity=1)
        return machines[resourceId].request()

# Helper function to check if operator is available
def check_operator_availability(operatorID, env, operators):
    if operatorID in operators:
        return operators[operatorID].request()
    else:
        operators[operatorID] = simpy.Resource(env, capacity=1)
        return operators[operatorID].request()

def process_job(job, env, machines, operators):
    # Request the machine
    release_time = string_to_timestamp(job["jobInputDate"])
    current_time = datetime.fromtimestamp(env.now) #.strftime('%Y-%m-%d %H:%M:%S')
    diff_delay = (release_time - current_time).total_seconds()
    yield env.timeout(diff_delay)
    with check_machine_availability(job['resourceId'], env, machines) as machine:
        yield machine
        job["productionStart"] = datetime.fromtimestamp(env.now).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} starts at {job['productionStart']}")
        # Check if the machine is broken
        if random.random() < 1.0: # 10% chance of machine breaking down
            print(f"Machine {job['resourceId']} broke down at {env.now}")
            repair_time = 120 * 60 # simulate repair time
            with check_operator_availability(job['operatorID'], env, operators) as operator:
                yield operator
                yield env.timeout(repair_time)
                print(f"Machine {job['resourceId']} fixed by operator {job['operatorID']} at {env.now}")

        # Job processing time
        processing_time = job["productionDuration"] * 60
        yield env.timeout(processing_time)
        job["productionEnd"] = datetime.fromtimestamp(env.now).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Job {job['jobID']} for Part {job['partID']} on Machine {job['resourceId']} ends at {job['productionEnd']}")

        start_time_comp = datetime.strptime(job["productionStart"], "%Y-%m-%d %H:%M:%S")
        release_date_comp = datetime.strptime(job["jobInputDate"], "%Y-%m-%d %H:%M:%S")
        end_time_comp = datetime.strptime(job["productionEnd"], "%Y-%m-%d %H:%M:%S")
        deadline_comp = datetime.strptime(job["deadlineDate"], "%Y-%m-%d %H:%M:%S")

        if start_time_comp > release_date_comp:
          job["jobStartDelay"] = str(start_time_comp - release_date_comp)
          job_start_delays.append(job["jobStartDelay"])
        
        if end_time_comp > deadline_comp:
          job["jobEndDelay"] = str(end_time_comp - deadline_comp)
          deadlin_exceeded.append(job["jobEndDelay"])
          
# Job data
job_list = [
  {
    "": 0,
    "jobID": 0,
    "partID": "P0",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-01 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 323.96,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 1,
    "jobID": 1,
    "partID": "P1",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-02 00:00:00",
    "deadlineDate": "2022-05-02 08:54:00",
    "productionDuration": 147.19,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 2,
    "jobID": 2,
    "partID": "P2",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-03 00:00:00",
    "deadlineDate": "2022-05-02 08:54:00",
    "productionDuration": 124.49,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 3,
    "jobID": 3,
    "partID": "P3",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-04 00:00:00",
    "deadlineDate": "2022-05-02 08:54:00",
    "productionDuration": 104.03,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 4,
    "jobID": 4,
    "partID": "P4",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-09-05 00:00:00",
    "deadlineDate": "2022-05-05 08:54:00",
    "productionDuration": 570.94,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 5,
    "jobID": 5,
    "partID": "P5",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-09-06 00:00:00",
    "deadlineDate": "2022-05-05 08:54:00",
    "productionDuration": 75.24,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 6,
    "jobID": 6,
    "partID": "P6",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-09-07 00:00:00",
    "deadlineDate": "2022-05-05 08:54:00",
    "productionDuration": 53.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 7,
    "jobID": 7,
    "partID": "P7",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-09-08 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 42.59,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 8,
    "jobID": 8,
    "partID": "P8",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-09 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 19.68,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 9,
    "jobID": 9,
    "partID": "P9",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-09-10 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 19.9,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 10,
    "jobID": 10,
    "partID": "P10",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-11 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 19.55,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 11,
    "jobID": 11,
    "partID": "P11",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-12 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 17.98,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 12,
    "jobID": 12,
    "partID": "P12",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-09-13 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 15.66,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 13,
    "jobID": 13,
    "partID": "P13",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-14 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 273.46,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 14,
    "jobID": 14,
    "partID": "P14",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-15 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 55.77,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 15,
    "jobID": 15,
    "partID": "P15",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-16 00:00:00",
    "deadlineDate": "2022-05-06 03:09:00",
    "productionDuration": 38.26,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 16,
    "jobID": 16,
    "partID": "P16",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-17 00:00:00",
    "deadlineDate": "2022-05-06 03:09:00",
    "productionDuration": 36.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 17,
    "jobID": 17,
    "partID": "P17",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-18 00:00:00",
    "deadlineDate": "2022-05-06 03:09:00",
    "productionDuration": 49.78,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 18,
    "jobID": 18,
    "partID": "P18",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-19 00:00:00",
    "deadlineDate": "2022-05-06 09:09:00",
    "productionDuration": 79.87,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 19,
    "jobID": 19,
    "partID": "P19",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-20 00:00:00",
    "deadlineDate": "2022-05-06 09:09:00",
    "productionDuration": 206.55,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 20,
    "jobID": 20,
    "partID": "P20",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-21 00:00:00",
    "deadlineDate": "2022-05-06 09:09:00",
    "productionDuration": 15.2,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 21,
    "jobID": 21,
    "partID": "P21",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-22 00:00:00",
    "deadlineDate": "2022-05-10 08:54:00",
    "productionDuration": 300.61,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 22,
    "jobID": 22,
    "partID": "P22",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-23 00:00:00",
    "deadlineDate": "2022-05-10 08:54:00",
    "productionDuration": 34.39,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 23,
    "jobID": 23,
    "partID": "P23",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-09-24 00:00:00",
    "deadlineDate": "2022-05-05 20:49:00",
    "productionDuration": 16,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 24,
    "jobID": 24,
    "partID": "P21",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-09-25 00:00:00",
    "deadlineDate": "2022-05-10 08:54:00",
    "productionDuration": 243.21,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 25,
    "jobID": 25,
    "partID": "P24",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-26 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 156.16,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 26,
    "jobID": 26,
    "partID": "P14",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-27 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 34.39,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 27,
    "jobID": 27,
    "partID": "P25",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-28 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 170.01,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 28,
    "jobID": 28,
    "partID": "P26",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-29 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 36.03,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 29,
    "jobID": 29,
    "partID": "P27",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-09-30 00:00:00",
    "deadlineDate": "2022-05-16 08:54:00",
    "productionDuration": 19.05,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 30,
    "jobID": 30,
    "partID": "P19",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-01 00:00:00",
    "deadlineDate": "2022-05-16 08:54:00",
    "productionDuration": 206.55,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 31,
    "jobID": 31,
    "partID": "P28",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-02 00:00:00",
    "deadlineDate": "2022-05-16 08:54:00",
    "productionDuration": 16.81,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 32,
    "jobID": 32,
    "partID": "P1",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-03 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 203.27,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 33,
    "jobID": 33,
    "partID": "P29",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-04 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 92.85,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 34,
    "jobID": 34,
    "partID": "P30",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-05 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 55.77,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 35,
    "jobID": 35,
    "partID": "P31",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-10-06 00:00:00",
    "deadlineDate": "2022-05-06 09:09:00",
    "productionDuration": 306.58,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 36,
    "jobID": 36,
    "partID": "P32",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-10-07 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 306.58,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 37,
    "jobID": 37,
    "partID": "P33",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-10-08 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 52.02,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 38,
    "jobID": 38,
    "partID": "P34",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-10-09 00:00:00",
    "deadlineDate": "2022-05-13 03:09:00",
    "productionDuration": 31.73,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 39,
    "jobID": 39,
    "partID": "P35",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-10-10 00:00:00",
    "deadlineDate": "2022-05-16 08:54:00",
    "productionDuration": 31.12,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 40,
    "jobID": 40,
    "partID": "P36",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2021-10-11 00:00:00",
    "deadlineDate": "2022-05-10 08:54:00",
    "productionDuration": 121.28,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 41,
    "jobID": 41,
    "partID": "P37",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-10-12 00:00:00",
    "deadlineDate": "2022-05-10 08:54:00",
    "productionDuration": 126.94,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 42,
    "jobID": 42,
    "partID": "P38",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-10-13 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 40.79,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 43,
    "jobID": 43,
    "partID": "P39",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-10-14 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 16.43,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 44,
    "jobID": 44,
    "partID": "P40",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-10-15 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 190.9,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 45,
    "jobID": 45,
    "partID": "P41",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-10-16 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 16.48,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 46,
    "jobID": 46,
    "partID": "P42",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2021-10-17 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 357.73,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 47,
    "jobID": 47,
    "partID": "P43",
    "resourceId": "M6","operatorID": "O2",
    "jobInputDate": "2021-10-18 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 1669.83,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 48,
    "jobID": 48,
    "partID": "P44",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-10-19 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 62.85,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 49,
    "jobID": 49,
    "partID": "P45",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-10-20 00:00:00",
    "deadlineDate": "2022-05-16 08:54:00",
    "productionDuration": 41.33,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 50,
    "jobID": 50,
    "partID": "P1",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-21 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 203.27,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 51,
    "jobID": 51,
    "partID": "P29",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-22 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 92.85,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 52,
    "jobID": 52,
    "partID": "P46",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-23 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 15.2,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 53,
    "jobID": 53,
    "partID": "P47",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-24 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 15.18,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 54,
    "jobID": 54,
    "partID": "P0",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2021-10-25 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 223.96,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 55,
    "jobID": 55,
    "partID": "P48",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-26 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 181.27,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 56,
    "jobID": 56,
    "partID": "P14",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-27 00:00:00",
    "deadlineDate": "2022-05-20 03:09:00",
    "productionDuration": 90.91,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 57,
    "jobID": 57,
    "partID": "P49",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-28 00:00:00",
    "deadlineDate": "2022-05-20 03:09:00",
    "productionDuration": 63.53,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 58,
    "jobID": 58,
    "partID": "P50",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-29 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 15.72,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 59,
    "jobID": 59,
    "partID": "P13",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-30 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 207.35,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 60,
    "jobID": 60,
    "partID": "P22",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-10-31 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 55.77,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 61,
    "jobID": 61,
    "partID": "P51",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-01 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 51.66,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 62,
    "jobID": 62,
    "partID": "P52",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-02 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 19.9,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 63,
    "jobID": 63,
    "partID": "P20",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-03 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 15.19,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 64,
    "jobID": 64,
    "partID": "P53",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-04 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 15.03,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 65,
    "jobID": 65,
    "partID": "P54",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-11-05 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 16.31,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 66,
    "jobID": 66,
    "partID": "P25",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-06 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 198.59,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 67,
    "jobID": 67,
    "partID": "P22",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-07 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 55.77,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 68,
    "jobID": 68,
    "partID": "P34",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-08 00:00:00",
    "deadlineDate": "2022-05-20 03:09:00",
    "productionDuration": 87.91,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 69,
    "jobID": 69,
    "partID": "P55",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-09 00:00:00",
    "deadlineDate": "2022-05-20 03:09:00",
    "productionDuration": 55.14,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 70,
    "jobID": 70,
    "partID": "P56",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-11-10 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 15.82,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 71,
    "jobID": 71,
    "partID": "P57",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-11-11 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 15.73,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 72,
    "jobID": 72,
    "partID": "P58",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2021-11-12 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 199.12,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 73,
    "jobID": 73,
    "partID": "P43",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-11-13 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 1911.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 74,
    "jobID": 74,
    "partID": "P42",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-11-14 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 125.24,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 75,
    "jobID": 75,
    "partID": "P59",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2021-11-15 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 35.01,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 76,
    "jobID": 76,
    "partID": "P42",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-11-16 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 1167.43,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 77,
    "jobID": 77,
    "partID": "P60",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-11-17 00:00:00",
    "deadlineDate": "2022-05-20 03:09:00",
    "productionDuration": 117,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 78,
    "jobID": 78,
    "partID": "P61",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-11-18 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 16.11,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 79,
    "jobID": 79,
    "partID": "P62",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-19 00:00:00",
    "deadlineDate": "2022-05-20 09:09:00",
    "productionDuration": 49.45,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 80,
    "jobID": 80,
    "partID": "P63",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-11-20 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 16.26,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 81,
    "jobID": 81,
    "partID": "P64",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-11-21 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 76.48,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 82,
    "jobID": 82,
    "partID": "P65",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-22 00:00:00",
    "deadlineDate": "2022-05-16 08:54:00",
    "productionDuration": 1088.97,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 83,
    "jobID": 83,
    "partID": "P66",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-11-23 00:00:00",
    "deadlineDate": "2022-05-17 08:54:00",
    "productionDuration": 840.33,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 84,
    "jobID": 84,
    "partID": "P67",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-24 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 383.7,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 85,
    "jobID": 85,
    "partID": "P68",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-25 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 136.59,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 86,
    "jobID": 86,
    "partID": "P69",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-26 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 118.15,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 87,
    "jobID": 87,
    "partID": "P70",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-27 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 139.07,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 88,
    "jobID": 88,
    "partID": "P71",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-11-28 00:00:00",
    "deadlineDate": "2022-05-19 20:49:00",
    "productionDuration": 94.01,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 89,
    "jobID": 89,
    "partID": "P25",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-29 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 192.56,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 90,
    "jobID": 90,
    "partID": "P22",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-11-30 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 55.77,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 91,
    "jobID": 91,
    "partID": "P2",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-01 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 38.87,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 92,
    "jobID": 92,
    "partID": "P72",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-02 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 17.09,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 93,
    "jobID": 93,
    "partID": "P29",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-03 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 92.85,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 94,
    "jobID": 94,
    "partID": "P73",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-04 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 36.57,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 95,
    "jobID": 95,
    "partID": "P74",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-05 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 25.62,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 96,
    "jobID": 96,
    "partID": "P75",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-06 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 50.89,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 97,
    "jobID": 97,
    "partID": "P26",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-07 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 183.49,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 98,
    "jobID": 98,
    "partID": "P13",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-08 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 109.17,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 99,
    "jobID": 99,
    "partID": "P14",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-09 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 34.39,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 100,
    "jobID": 100,
    "partID": "P17",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-10 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 29.75,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 101,
    "jobID": 101,
    "partID": "P76",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-11 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 38.1,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 102,
    "jobID": 102,
    "partID": "P77",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-12 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 31.22,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 103,
    "jobID": 103,
    "partID": "P78",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2021-12-13 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 201.41,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 104,
    "jobID": 104,
    "partID": "P79",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2021-12-14 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 198.71,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 105,
    "jobID": 105,
    "partID": "P80",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2021-12-15 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 184.35,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 106,
    "jobID": 106,
    "partID": "P81",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2021-12-16 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 117.95,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 107,
    "jobID": 107,
    "partID": "P2",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2021-12-17 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 86.66,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 108,
    "jobID": 108,
    "partID": "P5",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2021-12-18 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 110.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 109,
    "jobID": 109,
    "partID": "P82",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2021-12-19 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 51.04,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 110,
    "jobID": 110,
    "partID": "P83",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2021-12-20 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 15.35,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 111,
    "jobID": 111,
    "partID": "P84",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-12-21 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 106.87,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 112,
    "jobID": 112,
    "partID": "P31",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-12-22 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 1923.63,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 113,
    "jobID": 113,
    "partID": "P34",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-12-23 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 31.73,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 114,
    "jobID": 114,
    "partID": "P85",
    "resourceId": "M6","operatorID": "O2",
    "jobInputDate": "2021-12-24 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 50.54,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 115,
    "jobID": 115,
    "partID": "P86",
    "resourceId": "M6","operatorID": "O2",
    "jobInputDate": "2021-12-25 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 18.22,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 116,
    "jobID": 116,
    "partID": "P87",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2021-12-26 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 62.97,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 117,
    "jobID": 117,
    "partID": "P44",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-12-27 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 49.38,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 118,
    "jobID": 118,
    "partID": "P88",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2021-12-28 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 47.75,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 119,
    "jobID": 119,
    "partID": "P89",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-12-29 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 19.83,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 120,
    "jobID": 120,
    "partID": "P90",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-12-30 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 21.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 121,
    "jobID": 121,
    "partID": "P38",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2021-12-31 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 20.02,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 122,
    "jobID": 122,
    "partID": "P65",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-01 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 909.31,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 123,
    "jobID": 123,
    "partID": "P68",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-02 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 136.59,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 124,
    "jobID": 124,
    "partID": "P65",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-03 00:00:00",
    "deadlineDate": "2022-05-30 08:54:00",
    "productionDuration": 1088.97,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 125,
    "jobID": 125,
    "partID": "P91",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2022-01-04 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 2572.09,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 126,
    "jobID": 126,
    "partID": "P92",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2022-01-05 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 124.61,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 127,
    "jobID": 127,
    "partID": "P93",
    "resourceId": "M6","operatorID": "O2",
    "jobInputDate": "2022-01-06 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 606.03,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 128,
    "jobID": 128,
    "partID": "P94",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2022-01-07 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 15.72,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 129,
    "jobID": 129,
    "partID": "P95",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2022-01-08 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 1879.07,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 130,
    "jobID": 130,
    "partID": "P96",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2022-01-09 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 2366.81,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 131,
    "jobID": 131,
    "partID": "P97",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-10 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 8945.19,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 132,
    "jobID": 132,
    "partID": "P98",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-11 00:00:00",
    "deadlineDate": "2022-05-12 20:49:00",
    "productionDuration": 8440.2,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 133,
    "jobID": 133,
    "partID": "P99",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-12 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 1535.47,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 134,
    "jobID": 134,
    "partID": "P99",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-13 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 1643.36,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 135,
    "jobID": 135,
    "partID": "P99",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-14 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 1643.36,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 136,
    "jobID": 136,
    "partID": "P99",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-15 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 1643.36,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 137,
    "jobID": 137,
    "partID": "P99",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-01-16 00:00:00",
    "deadlineDate": "2022-05-23 08:54:00",
    "productionDuration": 1643.36,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 138,
    "jobID": 138,
    "partID": "P100",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-17 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 568.69,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 139,
    "jobID": 139,
    "partID": "P100",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-18 00:00:00",
    "deadlineDate": "2022-05-25 02:54:00",
    "productionDuration": 568.69,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 140,
    "jobID": 140,
    "partID": "P101",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-19 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 533.69,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 141,
    "jobID": 141,
    "partID": "P102",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-20 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 368.47,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 142,
    "jobID": 142,
    "partID": "P103",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-21 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 506.18,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 143,
    "jobID": 143,
    "partID": "P104",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-22 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 484.12,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 144,
    "jobID": 144,
    "partID": "P101",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-23 00:00:00",
    "deadlineDate": "2022-05-13 09:09:00",
    "productionDuration": 533.69,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 145,
    "jobID": 145,
    "partID": "P105",
    "resourceId": "M8","operatorID": "O1",
    "jobInputDate": "2022-01-24 00:00:00",
    "deadlineDate": "2022-05-24 08:54:00",
    "productionDuration": 318.53,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 146,
    "jobID": 146,
    "partID": "P106",
    "resourceId": "M9","operatorID": "O1",
    "jobInputDate": "2022-01-25 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 254.44,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 147,
    "jobID": 147,
    "partID": "P107",
    "resourceId": "M8","operatorID": "O1",
    "jobInputDate": "2022-01-26 00:00:00",
    "deadlineDate": "2022-05-24 20:49:00",
    "productionDuration": 67.34,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 148,
    "jobID": 148,
    "partID": "P78",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2022-01-27 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 201.39,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 149,
    "jobID": 149,
    "partID": "P79",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2022-01-28 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 196.68,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 150,
    "jobID": 150,
    "partID": "P80",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-29 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 184.35,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 151,
    "jobID": 151,
    "partID": "P81",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-01-30 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 175.14,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 152,
    "jobID": 152,
    "partID": "P2",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-01-31 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 86.66,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 153,
    "jobID": 153,
    "partID": "P5",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-02-01 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 110.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 154,
    "jobID": 154,
    "partID": "P7",
    "resourceId": "M7","operatorID": "O2",
    "jobInputDate": "2022-02-02 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 59.2,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 155,
    "jobID": 155,
    "partID": "P108",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-03 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 15.47,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 156,
    "jobID": 156,
    "partID": "P109",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-04 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 46.84,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 157,
    "jobID": 157,
    "partID": "P110",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-05 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 15.51,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 158,
    "jobID": 158,
    "partID": "P111",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-06 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 15.3,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 159,
    "jobID": 159,
    "partID": "P112",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-07 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 15.19,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 160,
    "jobID": 160,
    "partID": "P30",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-08 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 305.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 161,
    "jobID": 161,
    "partID": "P13",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-09 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 173.29,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 162,
    "jobID": 162,
    "partID": "P113",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-10 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 106.6,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 163,
    "jobID": 163,
    "partID": "P114",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-11 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 71.73,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 164,
    "jobID": 164,
    "partID": "P115",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-12 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 48.35,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 165,
    "jobID": 165,
    "partID": "P116",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-13 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 17.61,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 166,
    "jobID": 166,
    "partID": "P117",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-14 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 28.12,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 167,
    "jobID": 167,
    "partID": "P118",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-15 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 25.49,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 168,
    "jobID": 168,
    "partID": "P119",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-16 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 18.22,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 169,
    "jobID": 169,
    "partID": "P120",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2022-02-17 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 15.55,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 170,
    "jobID": 170,
    "partID": "P121",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-18 00:00:00",
    "deadlineDate": "2022-06-03 15:09:00",
    "productionDuration": 31.22,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 171,
    "jobID": 171,
    "partID": "P22",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-19 00:00:00",
    "deadlineDate": "2022-06-03 15:09:00",
    "productionDuration": 114.24,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 172,
    "jobID": 172,
    "partID": "P122",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-20 00:00:00",
    "deadlineDate": "2022-06-03 15:09:00",
    "productionDuration": 26.8,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 173,
    "jobID": 173,
    "partID": "P3",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-21 00:00:00",
    "deadlineDate": "2022-06-07 08:54:00",
    "productionDuration": 100.75,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 174,
    "jobID": 174,
    "partID": "P123",
    "resourceId": "M0","operatorID": "O1",
    "jobInputDate": "2022-02-22 00:00:00",
    "deadlineDate": "2022-06-07 08:54:00",
    "productionDuration": 96.32,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 175,
    "jobID": 175,
    "partID": "P33",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2022-02-23 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 128.06,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 176,
    "jobID": 176,
    "partID": "P36",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2022-02-24 00:00:00",
    "deadlineDate": "2022-05-31 08:54:00",
    "productionDuration": 69.15,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 177,
    "jobID": 177,
    "partID": "P37",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2022-02-25 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 634.67,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 178,
    "jobID": 178,
    "partID": "P40",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2022-02-26 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 554.12,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 179,
    "jobID": 179,
    "partID": "P124",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-02-27 00:00:00",
    "deadlineDate": "2022-06-02 20:49:00",
    "productionDuration": 157.15,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 180,
    "jobID": 180,
    "partID": "P125",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2022-02-28 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 15.18,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 181,
    "jobID": 181,
    "partID": "P43",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2022-03-01 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 1669.83,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 182,
    "jobID": 182,
    "partID": "P42",
    "resourceId": "M4","operatorID": "O2",
    "jobInputDate": "2022-03-02 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 125.24,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 183,
    "jobID": 183,
    "partID": "P60",
    "resourceId": "M1","operatorID": "O1",
    "jobInputDate": "2022-03-03 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 122.77,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 184,
    "jobID": 184,
    "partID": "P44",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2022-03-04 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 62.85,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 185,
    "jobID": 185,
    "partID": "P126",
    "resourceId": "M5","operatorID": "O2",
    "jobInputDate": "2022-03-05 00:00:00",
    "deadlineDate": "2022-06-03 03:09:00",
    "productionDuration": 37.52,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 186,
    "jobID": 186,
    "partID": "P127",
    "resourceId": "M2","operatorID": "O1",
    "jobInputDate": "2022-03-06 00:00:00",
    "deadlineDate": "2022-06-03 15:09:00",
    "productionDuration": 157.74,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 187,
    "jobID": 187,
    "partID": "P62",
    "resourceId": "M3","operatorID": "O1",
    "jobInputDate": "2022-03-07 00:00:00",
    "deadlineDate": "2022-06-03 15:09:00",
    "productionDuration": 32.9,
    "productionStart": "",
    "productionEnd": ""
  },
  {
    "": 188,
    "jobID": 188,
    "partID": "P38",
    "resourceId": "M6","operatorID": "O2",
    "jobInputDate": "2022-03-08 00:00:00",
    "deadlineDate": "2022-06-03 15:09:00",
    "productionDuration": 2720.18,
    "productionStart": "",
    "productionEnd": ""
  }
]

env = simpy.Environment()

machines = {
    "M0": simpy.Resource(env, capacity=1),
    "M1": simpy.Resource(env, capacity=1),
    "M2": simpy.Resource(env, capacity=1),
    "M3": simpy.Resource(env, capacity=1),
    "M4": simpy.Resource(env, capacity=1),
    "M5": simpy.Resource(env, capacity=1),
    "M6": simpy.Resource(env, capacity=1),
    "M7": simpy.Resource(env, capacity=1),
    "M8": simpy.Resource(env, capacity=1),
    "M9": simpy.Resource(env, capacity=1)
}

# Create a dictionary of operators
operators = {
    "O1": simpy.Resource(env, capacity=1),
    "O2": simpy.Resource(env, capacity=1)
}

job_start_delays = []
deadlin_exceeded = []
random.shuffle(job_list)
job_list = job_list

for job in job_list:
    env.process(process_job(job, env, machines, operators))

env.run()

print("Deadline exceeded for these many jobs: ", len(deadlin_exceeded))
print("These are the job IDs of those jobs: ", deadlin_exceeded)
print("Start delay for these many jobs: ", len(job_start_delays))
print("job_start_delays: ", job_start_delays)