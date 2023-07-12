import pandas as pd

import datetime

from pyomo.environ import *
from pyomo.gdp import *

from shift import ShiftModel


# TODO: Manual labor
# TODO: Consider case with different shifts in table, right now the shift of the first job is taken which is dumb
# TODO: Plan for just one week and ignore already planned jobs
# TODO: Bug where each job begins one hour later (conversion between seconds and datetime?)


def opt_schedule(df, starttime, missed_deadline_punish=5):
    """Optimizes a schedule using an optimizer and returns it as dataframe.

    Model taken from https://ojs.aaai.org/index.php/ICAPS/article/view/13596/13445
    """
    # planning of all jobs starts at the given starttime, all jobs that have
    # not been planned yet, get their start times increased to starttime
    if not isinstance(starttime, datetime.datetime):
        raise ValueError(
            f"starttime parameter needs to be datetime object. Given: {type(starttime)}"
        )
    # Assert that all necessary columns are in the dataframe
    necessary_columns = set(
        [
            "order_release",
            "machines",
            "duration_machine",
            "setup_time",
            "tool",
            "shift",
            "deadline",
        ]
    )
    if not necessary_columns.issubset(df.columns):
        raise ValueError(
            "Given DataFrame does not have all the necessary columns. "
            + f"Missing columns: {necessary_columns - df.columns}"
        )
    df["order_release"] = df["order_release"].apply(
        lambda x: starttime if x < starttime else x
    )

    machines = set(
        [
            machine
            for machine_list in df["machines"].tolist()
            for machine in machine_list.split(",")
            if machine != ""
        ]
    )
    company = df.attrs["company_name"]
    if not company:
        raise ValueError(
            "Given DataFrame does not contain the company name as attribute."
        )
    amount_of_jobs = len(df.index)
    jobs = range(amount_of_jobs)
    # All datetime values throughout this function need to be
    # converted to seconds, since pyomo does not calculate with datetimes.
    # Subtract setuptime from durations, since they are already part of that
    durations = {
        j: df.iloc[j]["duration_machine"].total_seconds()
        - df.iloc[j]["setup_time"].total_seconds()
        for j in jobs
    }
    first_release = df["order_release"].min().to_pydatetime()

    # Create setup time matrix for each job following one another
    setup_times = pd.DataFrame(
        [
            [
                df.iloc[j]["setup_time"].total_seconds()
                if df.iloc[j]["tool"] != df.iloc[i]["tool"] and i != j
                else 0
                for j in jobs
            ]
            for i in jobs
        ]
    )

    # Reduce deadline, since the jobs can't be worked on 24/7. By counting all
    # seconds from release to the deadline during all shift intervals, the
    # deadline gets reduced to release_in_seconds + seconds_to_deadline.
    # WARNING: Only works if all jobs have the same shift model, otherwise
    # they would be time-scaled differently
    deadlines = {}
    releases = {}
    shift_name = df.iloc[1]["shift"]
    for job_id in jobs:
        # Move release times based on total time in the shift
        shift = ShiftModel(company, shift_name, first_release)
        # Get earliest time the job can be worked on
        releases[job_id] = first_release.timestamp() + shift.count_time(
            first_release, df.iloc[job_id]["order_release"]
        )
        # Strip non-shift time from job duration and adjust deadline accordingly
        shift = ShiftModel(company, shift_name, df.iloc[job_id]["order_release"])
        deadlines[job_id] = releases[job_id] + shift.count_time(
            df.iloc[job_id]["order_release"], df.iloc[job_id]["deadline"]
        )

    # add dummy job with standard setup time if switching from dummy job to other job
    # otherwise 0. Dummy job has 0 duration
    setup_times[amount_of_jobs] = df.iloc[0]["setup_time"].total_seconds()
    setup_times.loc[amount_of_jobs] = 0
    durations[amount_of_jobs] = 0
    releases[amount_of_jobs] = first_release.timestamp()
    deadlines[amount_of_jobs] = df["deadline"].max().to_pydatetime()

    # create model
    m = ConcreteModel()

    # index set to simplify notation
    m.J = Set(initialize=jobs)
    m.J_dummy = Set(initialize=range(amount_of_jobs + 1))
    m.M = Set(initialize=machines)

    # each job is restricted to certain machines
    compatible_assignments = {
        (j, m) for j in jobs for m in machines if m in df.iloc[j]["machines"]
    }
    jobs_by_machine = {
        m: [j for j in jobs if m in df.iloc[j]["machines"]] for m in machines
    }
    m.JM = Set(within=m.J * m.M, initialize=compatible_assignments)
    m.M_relevant = [m for j in jobs for m in machines if m in df.iloc[j]["machines"]]

    # dummy job can run on all machines
    compatible_assignments_dummy = compatible_assignments
    compatible_assignments_dummy.update({(amount_of_jobs, m) for m in machines})
    for mach in jobs_by_machine.keys():
        jobs_by_machine[mach].append(amount_of_jobs)
    m.JM_dummy = Set(within=m.J_dummy * m.M, initialize=compatible_assignments_dummy)

    # Set of machines with compatible jobs
    m.J_by_M = Set(m.M, within=m.J_dummy, initialize=jobs_by_machine)

    # Pairs of jobs
    m.PAIRS = Set(initialize=m.J_dummy * m.J_dummy, dimen=2)
    # Pairs of jobs that can run on the same machine
    machine_pairs = [
        (j, k, mach)
        for j, k in m.PAIRS
        for mach in m.M
        if j in m.J_by_M[mach] and k in m.J_by_M[mach] and j != k
    ]
    m.MACH_PAIRS = Set(initialize=machine_pairs)
    # machine pairs without the dummy job as the second job, for constraint c6
    machine_pairs_no_dummy = [
        (j, k, mach)
        for j, k in m.PAIRS
        for mach in m.M
        if j in m.J_by_M[mach]
        and k in m.J_by_M[mach]
        and j != k
        and k != amount_of_jobs
    ]
    m.MACH_PAIRS_no_dummy = Set(initialize=machine_pairs_no_dummy)

    # decision variables
    m.completion = Var(m.J_dummy, domain=NonNegativeReals)
    m.completion_machine = Var(m.M, domain=NonNegativeReals)
    m.makespan = Var(bounds=(0, 2000000000))
    m.pastdue = Var(m.J, bounds=(0, 2000000000))
    m.early = Var(m.J, bounds=(0, 2000000000))

    # binary matrix whether job j is scheduled before job k on machine m
    m.x = Var(m.MACH_PAIRS, domain=Binary)

    m.pprint()

    # very large value for constraint c6
    big_m = max(releases) + sum(durations.values())

    # Objective. Additionally to makespan, also considers deadlines (pastdue)
    m.OBJ = Objective(
        expr=sum(m.pastdue[j] for j in m.J) * missed_deadline_punish
        + m.makespan
        - sum(m.early[j] for j in m.J),
        sense=minimize,
    )

    # define makespan
    m.c0 = Constraint(m.J, rule=lambda m, j: m.completion[j] <= m.makespan)
    # job starts after it is released
    # BUG: Jobs sometimes start a few minutes before their release
    m.c1 = Constraint(
        m.J,
        rule=lambda m, j: m.completion[j]
        - durations[j]
        - sum(
            setup_times[k][j] * m.x[k, j, mach]
            for k in m.J_dummy
            if j != k
            for mach in m.M
            if (k, j, mach) in machine_pairs
        )
        >= releases[j],
    )
    # every job has exactly one predecessor
    m.c2 = Constraint(
        m.J,
        rule=lambda m, k: sum(
            m.x[j, k, mach]
            for j in m.J_dummy
            if j != k
            for mach in m.M
            if (j, k, mach) in machine_pairs
        )
        == 1,
    )
    # each job has exactly one sucessor
    m.c3 = Constraint(
        m.J,
        rule=lambda m, j: sum(
            m.x[j, k, mach]
            for k in m.J_dummy
            if j != k
            for mach in m.M
            if (j, k, mach) in machine_pairs
        )
        == 1,
    )
    # at most one job is scheduled as the first job on each machine
    m.c4 = Constraint(
        m.M_relevant,
        rule=lambda m, mach: sum(
            m.x[amount_of_jobs, j, mach]
            for j in m.J
            if (amount_of_jobs, j, mach) in machine_pairs
        )
        <= 1,
    )
    # flow conservation constraint. If a job is scheduled on a machine, then a
    # predecessor and a successor must exist in the same machine
    m.c5 = Constraint(
        m.JM,
        rule=lambda m, j, mach: sum(
            m.x[j, k, mach]
            for k in m.J_dummy
            if j != k and (j, k, mach) in machine_pairs
        )
        - sum(
            m.x[k, j, mach]
            for k in m.J_dummy
            if j != k and (k, j, mach) in machine_pairs
        )
        == 0,
    )
    # right processing order, avoiding loops
    m.c6 = Constraint(
        m.MACH_PAIRS_no_dummy,
        rule=lambda m, j, k, mach: m.completion[k]
        - m.completion[j]
        + big_m * (1 - m.x[j, k, mach])
        >= setup_times[j][k] + durations[k],
    )
    # dummy job always starts and ends at time step 0
    m.completion[amount_of_jobs] = releases[amount_of_jobs]
    # compute, for each machine, time it finishes completion time
    m.c7 = Constraint(
        m.M,
        rule=lambda m, mach: sum(
            (setup_times[j][k] + durations[k]) * m.x[j, k, mach]
            for j in m.J_dummy
            for k in m.J
            if j != k
            if (j, k, mach) in machine_pairs
        )
        == m.completion_machine[mach],
    )
    # maximum completion time
    m.c8 = Constraint(
        m.M, rule=lambda m, mach: m.completion_machine[mach] <= m.makespan
    )

    # defines early and pastdue
    m.c9 = Constraint(
        m.J,
        rule=lambda m, j: m.completion[j] + m.early[j] == deadlines[j] + m.pastdue[j],
    )
    m.d1 = Disjunction(m.J, rule=lambda m, j: [m.early[j] == 0, m.pastdue[j] == 0])

    # apply gdp.hull to allow disjunctions
    transform = TransformationFactory("gdp.hull")
    transform.apply_to(m)

    SolverFactory("cbc").solve(m).write()

    # Enter schedule into dataframe
    df["calculated_setup_time"] = 0
    for j in m.J:
        # The resulting start is without the shifts, add the shift time back
        shift = ShiftModel(company, shift_name, first_release)
        # Check if setup time was added
        setup_time = 0
        machine = ""
        for jj, k, mach in m.x.keys():
            try:
                if k == j and pyomo.environ.value(m.x[jj, k, mach]):
                    # job jj ran right before j on the same machine
                    setup_time = setup_times[jj][k]
                    machine = mach
                    break
            except ValueError:
                # no value for current m.x
                continue

        final_start = shift.add_time(
            (m.completion[j]() - durations[j] - setup_time) / 60
            - first_release.timestamp() / 60
        )

        df.iat[int(j), df.columns.get_loc("calculated_start")] = final_start
        # Get calculated end by adding the time to the shift model of the job
        df.iat[int(j), df.columns.get_loc("calculated_end")] = shift.add_time(
            (durations[j] + setup_time) / 60
        )
        df.iat[int(j), df.columns.get_loc("selected_machine")] = machine
        df.iat[int(j), df.columns.get_loc("calculated_setup_time")] = setup_time / 60

    print(
        f"Planned jobs: {amount_of_jobs}. Missed deadlines: {sum(df['calculated_end'] > df['deadline'])}"
    )

    # temporarily write the result to planned start and end as well
    df["planned_start"] = df["calculated_start"]
    df["planned_end"] = df["calculated_end"]
    df["starttime"] = df["calculated_start"]
    df["endtime"] = df["calculated_end"]

    return df
