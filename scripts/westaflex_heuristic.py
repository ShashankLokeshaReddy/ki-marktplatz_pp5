import pandas as pd
import datetime
from enum import Enum
from orders import get_westaflex_orders
from orders import filter_orders
from orders import set_order_status
from orders import JobStatus
from job_summary import summarize_jobs
from visualization import gantt
from shift import ShiftModel


class PriorityProcedure(Enum):
    FIRST_COME_FIRST_SERVE = 1
    SHORTEST_OPERATION_TIME = 2
    LONGEST_OPERATION_TIME = 3


def get_date(datetime_object):
    """Extracts the date from a datetime object as a string.

    Args:
        datetime_object (_type_): The datetime object that contains the date

    Returns:
        _type_: A string, which contains the date
    """
    return str(datetime_object)[:11]


def combine_datetime_columns(df, col_name):
    """Combines two columns into one datetime column,
    where one column contains the date and one column contains the time.
    The date column is assumed to be in the col_name column and time is in the directly following column.
    The result will be stored in the col_name column.

    Args:
        df (_type_): A pandas dataframe containing the orders
        col_name (_type_): the selected column for datetime combination

    Returns:
        _type_: a pandas dataframe containing the orders with a combined datetime column
    """
    df[col_name] = df[col_name].apply(get_date) + df.iloc[
        :, df.columns.get_loc(col_name) + 1
    ].astype(str)
    df[col_name] = pd.to_datetime(df[col_name], errors="coerce")
    return df


def compute_priority_list(order_df, priority_procedure: PriorityProcedure):
    """Compute list of orders with highest to lowest priority according to a selected priority procedure.

    Args:
        order_df (_type_): pandas dataframe containing the orders
        priority_procedure (_type_): selected procedure to compute the priority list

    Raises:
        Exception: unknown priority procedure

    Returns:
        _type_: list ordered by priority for scheduling
    """
    if priority_procedure == PriorityProcedure.FIRST_COME_FIRST_SERVE:
        order_df["order_release"] = pd.to_datetime(order_df["order_release"])
        order_df = order_df.sort_values(by="order_release")
        return order_df["job"].tolist()
    elif priority_procedure == PriorityProcedure.SHORTEST_OPERATION_TIME:
        order_df = order_df.sort_values(by="duration_machine")
        return order_df["job"].tolist()
    elif priority_procedure == PriorityProcedure.LONGEST_OPERATION_TIME:
        order_df = order_df.sort_values(by="duration_machine", ascending=False)
        a = order_df["duration_machine"]
        return order_df["job"].tolist()
    else:
        raise Exception("Unknown priority procedure: " + priority_procedure)


def tool_setup_time(order_df, job, job_prev=""):
    """Computes the setup time for a job. If previous job is given, no setup time might be required.

    Args:
        order_df (_type_): pandas dataframe containing the orders
        job (_type_): id of the job whose setup time shall be computed
        job_prev (str, optional): id of a previous job if given. Defaults to ''.

    Returns:
        _type_: setup time given in minutes.
    """
    order = order_df.loc[order_df["job"] == job]
    # if no previous job exists, return setup time for job
    if not job_prev:
        return order["setuptime_material"].values[0]
    order_prev = order_df.loc[order_df["job"] == job_prev]
    if (
        order_prev["tube_type"].values[0] == order["tube_type"].values[0]
        and order_prev["tool"].values[0] == order["tool"].values[0]
    ):
        return 0
    else:
        return order["setuptime_material"].values[0]


def compute_job_period(shift_model, order_df, start_time, job, prev_job=""):
    """Compute end datetime for job execution including setup time, machine time and manual time.

    Args:
        order_df (_type_): pandas dataframe containing the orders
        starttime (_type_): datetime of job start
        job (_type_): id of the job to be executed
        prev_job (_type_): previous job on the same machine if given

    Returns:
        _type_: datetime of job ending
    """
    order = order_df.loc[order_df["job"] == job]
    setuptime_material = tool_setup_time(order_df, job, prev_job)
    setuptime_coil = order["setuptime_coil"].values[0]
    duration_machine = order["duration_machine"].values[0]
    duration_manual = order["duration_manual"].values[0]

    # compute work time
    duration_machine = duration_machine - setuptime_material
    if duration_machine > duration_manual:
        work_time = setuptime_coil + setuptime_material + duration_machine
    else:
        work_time = setuptime_coil + setuptime_material + duration_manual
        
    work_time_minutes = work_time.item() / 60000000000

    (job_period_start, job_period_end) = shift_model.compute_work_period(
        start_time, work_time_minutes
    )
    return (setuptime_material, job_period_start, job_period_end)


def schedule_orders(
    shift_model,
    order_df,
    priority_list,
    planning_period_start,
    planning_period_end,
):
    """Schedule the orders according to their priority to the available machines.
    Add planning information to dataframe.

    Args:
        order_df (_type_): pandas dataframe containing the orders
        order_machine_mapping (_type_): mapping from jobs to available machines
        priority_list (_type_): list of jobs ordered by priority
        planning_period_start (_type_): start of the planning period
        planning_period_end (_type_): end of the planning period

    Returns:
        _type_: pandas dataframe of the orders, where all orders within of planning period are planned.
    """
    # initiate machine jobs
    order_df["selected_machine"] = -1
    machine_endtime = {}
    machine_last_job = {}
    for machine in (
        "1531",
        "1532",
        "1533",
        "1534",
        "1535",
        "1536",
        "1537",
        "1541",
        "1542",
        "1543",
    ):
        machine_endtime[machine] = planning_period_start
        machine_last_job[machine] = ""

    # add planned and running jobs
    for job in order_df.loc[order_df["status"] == JobStatus.IN_PROGRESS].iterrows():
        assigned_machine = job['machine'].split(',')[0]
        if job["final_end"] > machine_endtime[assigned_machine]:
            machine_endtime[assigned_machine] = job["final_end"]
            machine_last_job[assigned_machine] = job
    for job in order_df.loc[order_df["status"] == JobStatus.PLANNED].iterrows():
        assigned_machine = job['machine'].split(',')[0]
        if job["planned_end"] > machine_endtime[assigned_machine]:
            machine_endtime[assigned_machine] = job["planned_end"]
            machine_last_job[assigned_machine] = job

    # iterate over prioritized jobs
    for job in priority_list:
        machine_tmp_id = ""
        machine_tmp_setuptime = 0
        machine_tmp_starttime = pd.Timestamp("NaT").to_pydatetime()
        machine_tmp_endtime = pd.Timestamp("NaT").to_pydatetime()
        # iterate over possible machines
        job_machines = order_df.loc[order_df['job'] == job]['machines'].values[0]
        for machine in job_machines.split(','):
            (machine_curr_setuptime, machine_curr_starttime, machine_curr_endtime) = compute_job_period(
                shift_model,
                order_df,
                machine_endtime[machine],
                job,
                machine_last_job[machine],
            )
            if (
                pd.isnull(machine_tmp_endtime)
                or machine_curr_endtime < machine_tmp_endtime
            ):
                machine_tmp_id = machine
                machine_tmp_setuptime = machine_curr_setuptime
                machine_tmp_starttime = machine_curr_starttime
                machine_tmp_endtime = machine_curr_endtime

        # only consider jobs that can finish within the planning period
        if machine_tmp_endtime < planning_period_end:
            order_df.loc[
                (order_df["job"] == job), "calculated_start"
            ] = machine_tmp_starttime
            order_df.loc[
                (order_df["job"] == job), "calculated_end"
            ] = machine_tmp_endtime
            order_df.loc[
                (order_df["job"] == job), "planned_start"
            ] = machine_tmp_starttime
            order_df.loc[(order_df["job"] == job), "calculated_setup_time"] = machine_tmp_setuptime
            order_df.loc[(order_df["job"] == job), "planned_end"] = machine_tmp_endtime
            order_df.loc[(order_df["job"] == job), "selected_machine"] = machine_tmp_id
            machine_endtime[machine_tmp_id] = machine_tmp_endtime
            machine_last_job[machine_tmp_id] = job

    return order_df


# scheduling parameters
planning_period_start = datetime.datetime(2022, 3, 16, 8, 0, 0)  # 02.05.2020 0:00:00
planning_period_end = datetime.datetime(2022, 5, 8, 23, 59, 59)  # 08.05.22 23:59:59
priority_procedure = PriorityProcedure.FIRST_COME_FIRST_SERVE
shift_model_type = "W01S3"
company_name = "westaflex"

shift_model = ShiftModel(company_name, shift_model_type, planning_period_start)
order_df = get_westaflex_orders()
# TODO remove shortening of database for practical tests
order_df.drop(index=order_df.index[:180], axis=0, inplace=True)
order_df = filter_orders(order_df, planning_period_start, planning_period_end)
order_df = set_order_status(order_df)
# summarize jobs
order_df = summarize_jobs(order_df)
priority_list = compute_priority_list(order_df, priority_procedure)
order_df = schedule_orders(
    shift_model,
    order_df,
    priority_list,
    planning_period_start,
    planning_period_end,
)

# filter for planned jobs within the planning period
order_df = order_df[
    (pd.notnull(order_df["planned_start"])) & (pd.notnull(order_df["planned_end"]))
]

# visualize orders as gantt chart
gantt(order_df)

# show machine-specific schedule
order_df = order_df[order_df["selected_machine"] == "1534"]
order_df = order_df.sort_values(by="planned_start")
order_df = order_df.reset_index(drop=True)

# print results to console
print(order_df[["job", "selected_machine", "planned_start", "planned_end"]])
