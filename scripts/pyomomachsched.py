import pandas as pd

import matplotlib.pyplot as plt
import shutil
import sys
import os.path
import datetime
import logging

from pyomo.environ import *
from pyomo.gdp import *
from pyomo.util.infeasible import log_infeasible_constraints

from shift import ShiftModel


# TODO: Make compatible with datetimes and shift models
# TODO: Setuptime
# TODO: Combine orders
# TODO: Manual labor
# TODO: Plan for just one week
# TODO: Bug where each job begins one hour later (conversion between seconds and datetime?)


def opt_schedule(df, starttime, last_tool):
    """Optimizes a schedule using an optimizer and returns it as dataframe.

    Model taken from https://ojs.aaai.org/index.php/ICAPS/article/view/13596/13445
    """
    # TODO: generalize machines instead of hard coding them
    machines = ['1531', '1532', '1533', '1534',
                '1535', '1536', '1537', '1541', '1542', '1543']
    amount_of_jobs = len(df.index)
    jobs = range(amount_of_jobs)
    # All datetime values throughout this function need to be
    # converted to seconds, since pyomo does not calculate with datetimes
    durations = {j: df.iloc[j]['duration_machine'].total_seconds()
                 for j in jobs}
    first_release = df['order_release'].min().to_pydatetime()

    # Create setup time matrix for each job following one another
    setup_times = pd.DataFrame([[df.iloc[j]['setuptime_material'].total_seconds() + df.iloc[j]['setuptime_coil'].total_seconds()
                               if df.iloc[j]['tool'] != df.iloc[i]['tool'] and i != j else 0 for j in jobs] for i in jobs])

    # Reduce deadline, since the jobs can't be worked on 24/7. By counting all
    # seconds from release to the deadline during all shift intervals, the
    # deadline gets reduced to release_in_seconds + seconds_to_deadline.
    # WARNING: Only works if all jobs have the same shift model, otherwise
    # they would be time-scaled differently
    deadlines = {}
    releases = {}
    for job_id in jobs:
        # Move release times based on total time in the shift
        shift = ShiftModel(
            first_release, df.iloc[job_id]['shift_model'])
        # Get earliest time the job can be worked on
        releases[job_id] = first_release.timestamp() + shift.count_time(
            first_release, df.iloc[job_id]['order_release'])
        # Strip non-shift time from job duration and adjust deadline accordingly
        shift = ShiftModel(
            df.iloc[job_id]['order_release'], df.iloc[job_id]['shift_model'])
        deadlines[job_id] = releases[job_id] + shift.count_time(
            df.iloc[job_id]['order_release'], df.iloc[job_id]['deadline'])

    # add dummy job with standard setup time if switching from dummy job to other job
    # otherwise 0. Dummy job has 0 duration
    setup_times[amount_of_jobs] = df.iloc[0]['setuptime_material'].total_seconds(
    ) + df.iloc[0]['setuptime_coil'].total_seconds()
    setup_times.loc[amount_of_jobs] = 0
    print(setup_times)
    durations[amount_of_jobs] = 0
    releases[amount_of_jobs] = first_release.timestamp()
    deadlines[amount_of_jobs] = df['deadline'].max().to_pydatetime()

    # create model
    m = ConcreteModel()

    # index set to simplify notation
    m.J = Set(initialize=jobs)
    m.J_dummy = Set(initialize=range(amount_of_jobs + 1))
    m.M = Set(initialize=machines)

    # each job is restricted to certain machines
    compatible_assignments = {(j, m) for j in jobs
                              for m in machines
                              if m in df.iloc[j]['machine_selection']}
    jobs_by_machine = {m:
                       [j for j in jobs if m in df.iloc[j]['machine_selection']]
                       for m in machines}
    m.JM = Set(within=m.J * m.M, initialize=compatible_assignments)
    m.M_relevant = [m for j in jobs for m in machines if m in df.iloc[j]
                    ['machine_selection']]

    # dummy job can run on all machines
    compatible_assignments_dummy = compatible_assignments
    compatible_assignments_dummy.update(
        {(amount_of_jobs, m) for m in machines})
    for mach in jobs_by_machine.keys():
        jobs_by_machine[mach].append(amount_of_jobs)
    m.JM_dummy = Set(within=m.J_dummy * m.M,
                     initialize=compatible_assignments_dummy)

    # Set of machines with compatible jobs
    m.J_by_M = Set(m.M, within=m.J_dummy, initialize=jobs_by_machine)

    # Pairs of jobs
    m.PAIRS = Set(initialize=m.J_dummy * m.J_dummy, dimen=2)
    # Pairs of jobs that can run on the same machine
    machine_pairs = [(j, k, mach)
                     for j, k in m.PAIRS for mach in m.M if j in m.J_by_M[mach] and k in m.J_by_M[mach] and j != k]
    m.MACH_PAIRS = Set(initialize=machine_pairs)
    # machine pairs without the dummy job as the second job, for constraint c6
    machine_pairs_no_dummy = [(j, k, mach)
                              for j, k in m.PAIRS for mach in m.M if j in m.J_by_M[mach] and k in m.J_by_M[mach] and j != k and k != amount_of_jobs]
    m.MACH_PAIRS_no_dummy = Set(initialize=machine_pairs_no_dummy)

    # decision variables
    m.completion = Var(m.J_dummy, domain=NonNegativeReals)
    m.completion_machine = Var(m.M, domain=NonNegativeReals)
    m.makespan = Var(bounds=(0, 2000000000))

    # binary matrix whether job j is scheduled before job k on machine m
    m.x = Var(m.MACH_PAIRS, domain=Binary)

    # binary variables denoting which job will run first
    m.first = Var(m.JM, domain=Binary)

    m.pprint()

    # for modeling disjunctive constraints
    big_m = max(releases) + sum(durations.values())

    # Objective
    m.OBJ = Objective(expr=m.makespan, sense=minimize)

    # define makespan
    m.c0 = Constraint(m.J, rule=lambda m, j: m.completion[j] <= m.makespan)
    # job starts after it is released
    m.c1 = Constraint(m.J, rule=lambda m,
                      j: m.completion[j] - durations[j] >= releases[j])
    # every job has exactly one predecessor
    m.c2 = Constraint(m.J, rule=lambda m, k: sum(
        m.x[j, k, mach] for j in m.J_dummy if j != k for mach in m.M if (j, k, mach) in machine_pairs) == 1)
    # each job has exactly one sucessor
    m.c3 = Constraint(m.J, rule=lambda m, j: sum(
        m.x[j, k, mach] for k in m.J_dummy if j != k for mach in m.M if (j, k, mach) in machine_pairs) == 1)
    # at most one job is scheduled as the first job on each machine
    m.c4 = Constraint(m.M_relevant, rule=lambda m, mach: sum(
        m.x[amount_of_jobs, j, mach] for j in m.J if (amount_of_jobs, j, mach) in machine_pairs) <= 1)
    # flow conservation constraint. If a job is scheduled on a machine, then a
    # predecessor and a successor must exist in the same machine
    m.c5 = Constraint(m.JM, rule=lambda m, j, mach: sum(
        m.x[j, k, mach] for k in m.J_dummy
        if j != k and (j, k, mach) in machine_pairs) -
        sum(m.x[k, j, mach] for k in m.J_dummy
            if j != k and (k, j, mach) in machine_pairs) == 0)
    # right processing order, avoiding loops
    m.c6 = Constraint(m.MACH_PAIRS_no_dummy, rule=lambda m, j, k, mach:
                      m.completion[k] - m.completion[j] + big_m * (
                          1 - m.x[j, k, mach]) >= setup_times[j][k] + durations[k])
    # dummy job always starts and ends at time step 0
    m.completion[amount_of_jobs] = releases[amount_of_jobs]
    # compute, for each machine, time it finishes completion time
    m.c7 = Constraint(m.M, rule=lambda m, mach: sum(
        (setup_times[j][k] + durations[k]) * m.x[j, k, mach]
        for j in m.J_dummy for k in m.J if j != k
        if (j, k, mach) in machine_pairs) == m.completion_machine[mach])
    # maximum completion time
    m.c8 = Constraint(m.M, rule=lambda m,
                      mach: m.completion_machine[mach] <= m.makespan)

    SolverFactory('gurobi', solver_io="python").solve(m).write()
    log_infeasible_constraints(m, log_expression=True, log_variables=True)
    logging.basicConfig(filename='example.log',
                        encoding='utf-8', level=logging.INFO)

    # Enter schedule into dataframe
    df['setup_time'] = 0
    for j in m.J:
        # The resulting start is without the shifts, add the shift time back
        shift = ShiftModel(first_release, df.iloc[j]['shift_model'])
        # Check if setup time was added
        setup_time = 0
        machine = ''
        for jj, k, mach in m.x.keys():
            try:
                if k == j and pyomo.environ.value(m.x[jj, k, mach]):
                    print(f"jj: {jj}, k: {k}, mach: {mach}")
                    # job jj ran right before j on the same machine
                    setup_time = setup_times[jj][k]
                    machine = mach
                    break
            except ValueError:
                # no value for current m.x
                continue

        print(
            f"completion: {m.completion[j]()}, duration: {durations[j]}, setup_time: {setup_time}")
        actual_start = shift.add_time(
            (m.completion[j]() - durations[j] - setup_time) / 60 - first_release.timestamp() / 60)

        df.iat[int(j), df.columns.get_loc('calculated_start')
               ] = actual_start
        # Get calculated end by adding the time to the shift model of the job
        df.iat[int(j), df.columns.get_loc('calculated_end')
               ] = shift.add_time((durations[j] + setup_time) / 60)
        # Get chosen machine by iterating through m.z
        df.iat[int(j), df.columns.get_loc('machine')] = machine
        df.iat[int(j), df.columns.get_loc('setup_time')] = setup_time
        print(f'machine: {machine}, release: {releases[j]},\
            start: {m.completion[j]() - durations[j] - setup_time}, end: {m.completion[j]()}')

    return df
