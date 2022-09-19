import pandas as pd

import matplotlib.pyplot as plt
import shutil
import sys
import os.path
import datetime

from pyomo.environ import *
from pyomo.gdp import *

import termination
from shift import ShiftModel

"""
Model constraint definitions
----------------------
id_j : ID of task j
due_j : due time for task j
duration_j : duration of task j
release_j : when task j becomes available

start_j : start of task j
pastdue_j : time by which task j is past due
early_j : time by which task j is finished early


A job cannot start until it is released:
start_j >= release_j

Early and pastdue times should be aligned correctly:
start_j + duration_j + early_j = due_j + pastdue_j
early_j >= 0
pastdue_j >= 0

Each job should only run on one machine it has been assigned to,
indicated by z_j_m:
sum(z_j_m, over all m) = 1, for all j

Assure that for any jobs j and k that they don't run at the same time
on one machine. y_jk=1 indicates j finishes before k starts, else 0:
start_j + duration_j <= start_k + M*(y_jk + (1 - z_j_m) + (1 - z_k_m))
start_k + duration_k <= start_j + M*()
"""

# TODO: Make compatible with datetimes and shift models
# TODO: Setuptime
# TODO: Combine orders
# TODO: Manual labor
# TODO: Plan for just one week
# TODO: Bug where each job begins one hour later (conversion between seconds and datetime?)


def opt_schedule(df, starttime, last_tool):
    """Optimizes a schedule using an optimizer and returns it as dataframe.
    """
    # All datetime values throughout this function need to be
    # converted to seconds, since pyomo does not calculate with datetimes
    machines = ['1531', '1532', '1533', '1534',
                '1535', '1536', '1537', '1541', '1542', '1543']
    jobs = range(len(df.index))
    durations = {j: df.iloc[j]['duration_machine'].total_seconds()
                 for j in jobs}
    tools = {j: df.iloc[j]['tool'] for j in jobs}

    # Reduce deadline, since the jobs can't be worked on 24/7. By counting all
    # seconds from release to the deadline during all shift intervals, the
    # deadline gets reduced to release_in_seconds + seconds_to_deadline.
    deadlines = {}
    for job_id in jobs:
        shift = termination.ShiftModel(
            df.iloc[job_id]['order_release'], df.iloc[job_id]['shift_model'])
        deadlines[job_id] = df.iloc[job_id]['order_release'].timestamp() + shift.count_time(
            df.iloc[job_id]['order_release'], df.iloc[job_id]['deadline'])
    # create model
    m = ConcreteModel()

    # index set to simplify notation
    m.J = Set(initialize=jobs)
    m.M = Set(initialize=machines)

    # each job is restricted to certain machines
    compatible_assignments = {(j, m) for j in jobs
                              for m in machines
                              if m in df.iloc[j]['machine_selection']}
    jobs_by_machine = {m:
                       [j for j in jobs if m in df.iloc[j]['machine_selection']]
                       for m in machines}
    m.JM = Set(within=m.J * m.M, initialize=compatible_assignments)
    # Set of machines with compatible jobs
    m.J_by_M = Set(m.M, within=m.J, initialize=jobs_by_machine)

    # Pairs of jobs
    m.PAIRS = Set(initialize=m.J * m.J, dimen=2, filter=lambda m, j, k: j < k)
    # Pairs of jobs that can run on the same machine
    m.MACH_PAIRS = Set(initialize=[(j, k, mach)
                       for j, k in m.PAIRS for mach in m.M if j in m.J_by_M[mach] and k in m.J_by_M[mach]])

    # Tool for each job
    # m.TOOLS = Set(initialize={j: df.iloc[j]['tool'] for j in jobs})

    # Duration for each job
    # m.DURATIONS = Set(m.J, initialize={j: [df.iloc[j]['duration_machine'].total_seconds(
    # )] for j in jobs})

    # decision variables
    m.start = Var(m.J, bounds=(0, 2000000000))
    m.makespan = Var(domain=NonNegativeReals)
    m.pastdue = Var(m.J, bounds=(0, 2000000000))
    m.early = Var(m.J, bounds=(0, 2000000000))

    # additional decision variables for use in the objecive
    m.ispastdue = Var(m.J, domain=Binary)
    m.maxpastdue = Var(domain=NonNegativeReals)

    # for binary assignment of jobs to machines
    m.z = Var(m.JM, domain=Binary)

    # for binary assignment of setup times for each job
    m.setup = Var(m.J, domain=Binary)

    # for modeling disjunctive constraints
    big_m = max([df.iloc[j]['order_release'] for j in m.J]).timestamp() + \
        sum([duration for duration in durations.values()])

    # Objective and constraints
    m.OBJ = Objective(expr=sum(
        m.pastdue[j] for j in m.J) + m.makespan - sum(m.early[j] for j in m.J), sense=minimize)

    # job starts after it is released
    m.c1 = Constraint(m.J, rule=lambda m,
                      j: m.start[j] >= df.iloc[j]['order_release'].timestamp())

    # defines early and pastdue
    m.c2 = Constraint(m.J, rule=lambda m, j: m.start[j] + durations[j] +
                      m.early[j] == deadlines[j] + m.pastdue[j])
    m.d1 = Disjunction(m.J, rule=lambda m, j: [
        m.early[j] == 0, m.pastdue[j] == 0])

    # each job is assigned to one and only one machine
    # also only consider valid machines for each job
    m.c3 = Constraint(m.J, rule=lambda m, j: sum(
        m.z[j, mach] for mach in m.J_by_M if j in m.J_by_M[mach]) == 1)

    # defines a binary variable indicating if a job is past due
    m.c4 = Disjunction(m.J, rule=lambda m, j: [
        m.pastdue[j] == 0, m.ispastdue[j] == 1])

    # all jobs must be finished before max pastdue
    m.c5 = Constraint(m.J, rule=lambda m, j: m.pastdue[j] <= m.maxpastdue)

    # defining make span
    m.c6 = Constraint(m.J, rule=lambda m,
                      j: m.start[j] + durations[j] <= m.makespan)

    # subtract setup time if the same tool is used
    # TODO: Possible without setting any variables?
    # m.c7 = Constraint(m.MACH_PAIRS, m.J, rule=lambda m, j, k, mach, h: [])

    # disjuctions
    m.d0 = Disjunction(m.MACH_PAIRS, rule=lambda m, j, k, mach:
                       [m.start[j] + durations[j] <= m.start[k] + big_m * ((1 - m.z[j, mach]) + (1 - m.z[k, mach])),
                        m.start[k] + durations[k] <= m.start[j] + big_m * ((1 - m.z[j, mach]) + (1 - m.z[k, mach]))])

    # transform model to Generalized Disjunctive Programming, to allow disjunctions
    transform = TransformationFactory('gdp.hull')
    transform.apply_to(m)

    SolverFactory('cbc').solve(m).write()

    # Enter schedule into dataframe
    for j in m.J:
        shift = termination.ShiftModel(datetime.datetime.fromtimestamp(
            m.start[j]()), df.iloc[j]['shift_model'])

        # Convert timestep seconds back to datetime for start
        df.iat[int(j), df.columns.get_loc('calculated_start')
               ] = datetime.datetime.fromtimestamp(m.start[j]())
        # Get calculated end by adding the time to the shift model of the job
        df.iat[int(j), df.columns.get_loc('calculated_end')
               ] = shift.add_time(durations[j] / 60)
        # Get chosen machine by iterating through m.z
        df.iat[int(j), df.columns.get_loc('machine')] = [
            mach for mach in machines if j in m.J_by_M[mach] and pyomo.environ.value(m.z[j, mach])][0]

    # Temporary
    df['setup_time'] = 0

    return df
