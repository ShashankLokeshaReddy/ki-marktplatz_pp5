import pandas as pd
import pathlib
import os
import numpy as np
import datetime
from enum import Enum
from shift import ShiftModel

# project root path
PROJECT_PATH = pathlib.Path(__file__).parent.parent.resolve()
# path to data source file
DATA_SOURCE_PATH = os.path.join(PROJECT_PATH, "data", "20220706_Auftragsdatenbank.xlsm")
# sheet of source file containing database
DATA_SOURCE_SHEET = "Datenbank_Auftragsdaten"


class JobStatus(Enum):
    UNKNOWN = 1
    UNPLANNED = 2
    CALCULATED = 3
    PLANNED = 4
    IN_PROGRESS = 5


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
    """Combines two columns into one datetime column, where one column contains the date and one column contains the time.
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


def get_orders() -> pd.DataFrame:
    """Extract all necessary information from the original data source excel sheet.

    Returns:
        pd.DataFrame: pandas dataframe containing all orders and necessary information
    """
    # Read file
    order_df = pd.read_excel(DATA_SOURCE_PATH, DATA_SOURCE_SHEET)
    # Rename columns after sheet header
    order_df = order_df.rename(columns=order_df.iloc[10])
    # Ignore first 14 rows since data starts at row 15
    order_df = order_df.drop(np.arange(13))
    order_df = order_df.reset_index(drop=True)
    # Combine separate date time columns to datetime
    order_df = combine_datetime_columns(order_df, "Spätester Bearbeitungsbeginn")
    order_df = combine_datetime_columns(order_df, "spätester Fertigstellungszeitpunkt")
    order_df = combine_datetime_columns(order_df, "Berechneter Bearbei-tungsbeginn")
    order_df = combine_datetime_columns(
        order_df, "Berechneter Fertigstellungs-zeitpunkt"
    )
    order_df = combine_datetime_columns(order_df, "PLAN-Bearbeitungs-beginn")
    order_df = combine_datetime_columns(order_df, "PLAN-Fertigstellungs-zeitpunkt")
    order_df = combine_datetime_columns(order_df, "IST- Bearbeitungs-beginn")
    order_df = combine_datetime_columns(order_df, "IST-Fertigstellungs-zeitpunkt")
    # Name machine number colums appropriately
    order_df.columns.values[25] = "1531"
    order_df.columns.values[26] = "1532"
    order_df.columns.values[27] = "1533"
    order_df.columns.values[28] = "1534"
    order_df.columns.values[29] = "1535"
    order_df.columns.values[30] = "1536"
    order_df.columns.values[31] = "1537"
    order_df.columns.values[32] = "1541"
    order_df.columns.values[33] = "1542"
    order_df.columns.values[34] = "1543"
    # Name first column to reference it for deletion
    order_df = order_df.rename(columns={order_df.columns[0]: "Nichts"})
    order_df = order_df.drop("Nichts", axis=1)
    # get all important columns and rename them
    order_df = order_df[
        [
            "Fertigungsauf-tragsnummer",
            "Auftragseingabe-zeitpunkt",
            "Spätester Bearbeitungsbeginn",
            "Bearbeitungsdauer",
            "Dauer Handarbeit",
            "spätester Fertigstellungszeitpunkt",
            "Berechneter Bearbei-tungsbeginn",
            "Berechneter Fertigstellungs-zeitpunkt",
            "PLAN-Bearbeitungs-beginn",
            "PLAN-Fertigstellungs-zeitpunkt",
            "IST- Bearbeitungs-beginn",
            "IST-Fertigstellungs-zeitpunkt",
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
            "Rohrtyp",
            "Werkzeug-nummer",
            "Rüstzeit für WKZ/Materialwechsel",
            "Rüstzeit für Coilwechsel"
        ]
    ]
    order_df.rename(
        columns={
            "Fertigungsauf-tragsnummer": "job",
            "Auftragseingabe-zeitpunkt": "order_release",
            "Spätester Bearbeitungsbeginn": "deadline_start",
            "spätester Fertigstellungszeitpunkt": "deadline_end",
            "Berechneter Bearbei-tungsbeginn": "calculated_start",
            "Berechneter Fertigstellungs-zeitpunkt": "calculated_end",
            "PLAN-Bearbeitungs-beginn": "planned_start",
            "PLAN-Fertigstellungs-zeitpunkt": "planned_end",
            "IST- Bearbeitungs-beginn": "final_start",
            "IST-Fertigstellungs-zeitpunkt": "final_end",
            "Bearbeitungsdauer": "machine_time",
            "Dauer Handarbeit": "manual_time",
            "Rohrtyp": "tube_type",
            "Werkzeug-nummer": "tool",
            "Rüstzeit für WKZ/Materialwechsel": "setuptime_material",
            "Rüstzeit für Coilwechsel": "setuptime_coil"
        },
        inplace=True,
    )
    return order_df


# TODO filter out jobs marked with "R"
def filter_orders(order_df, planning_period_start, planning_period_end):
    """Removes orders, which are marked for removal and are scheduled outside of the planning period.
    Orders are outside of the planning period if they are already finished (final_end before planning_period_start) 
    or if they are planned after the planning period (planning_start after planning_period_end)

    Args:
        order_def (_type_): pandas dataframe containing the orders
        planning_period_start (_type_): start of planning period in datetime
        planning_period_end (_type_): end of planning period in datetime

    Returns:
        _type_: pandas dataframe of filtered orders
    """
    order_df = order_df[
        (pd.isnull(order_df["final_end"]))
        | (order_df["final_end"] > planning_period_start)
    ]
    order_df = order_df[
        (pd.isnull(order_df["planned_start"]))
        | (order_df["planned_start"] < planning_period_end)
    ]
    return order_df


def set_order_status(order_df):
    """Assign a job status to each order according to their time stamps.

    Args:
        order_df (_type_): pandas dataframe containing the orders

    Returns:
        _type_: pandas dataframe with an additional status column
    """
    order_df["status"] = JobStatus.UNKNOWN
    for idx in order_df.index:
        if pd.notnull(order_df.loc[idx, "deadline_start"]) and pd.notnull(
            order_df.loc[idx, "deadline_end"]
        ):
            order_df.loc[idx, "status"] = JobStatus.UNPLANNED
        if pd.notnull(order_df.loc[idx, "calculated_start"]) and pd.notnull(
            order_df.loc[idx, "calculated_end"]
        ):
            order_df.loc[idx, "status"] = JobStatus.CALCULATED
        if pd.isnull(order_df.loc[idx, "planned_start"]) and pd.notnull(
            order_df.loc[idx, "planned_end"]
        ):
            order_df.loc[idx, "status"] = JobStatus.PLANNED
        if pd.notnull(order_df.loc[idx, "final_start"]):
            order_df.loc[idx, "status"] = JobStatus.IN_PROGRESS
    # TODO compute final_end for orders in_work, where this is not given (order is finished in future)
    return order_df


def get_order_machine_mapping(order_df):
    """Parse the machines that are assigned to each order

    Args:
        order_df (_type_): pandas dataframe containing the orders

    Returns:
        _type_: mapping from orders to available machines
    """
    order_machine_mapping = {}
    for _, row in order_df.iterrows():
        auftrag_nr = row["job"]
        auftrag_machine_list = []
        if row["1531"] == "x":
            auftrag_machine_list.append("1531")
        if row["1532"] == "x":
            auftrag_machine_list.append("1532")
        if row["1533"] == "x":
            auftrag_machine_list.append("1533")
        if row["1534"] == "x":
            auftrag_machine_list.append("1534")
        if row["1535"] == "x":
            auftrag_machine_list.append("1535")
        if row["1536"] == "x":
            auftrag_machine_list.append("1536")
        if row["1537"] == "x":
            auftrag_machine_list.append("1537")
        if row["1541"] == "x":
            auftrag_machine_list.append("1541")
        if row["1542"] == "x":
            auftrag_machine_list.append("1542")
        if row["1543"] == "x":
            auftrag_machine_list.append("1543")
        order_machine_mapping[auftrag_nr] = auftrag_machine_list
    return order_machine_mapping


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
        order_df = order_df.sort_values(by="machine_time")
        return order_df["job"].tolist()
    elif priority_procedure == PriorityProcedure.LONGEST_OPERATION_TIME:
        order_df = order_df.sort_values(by="machine_time", ascending=False)
        a = order_df["machine_time"]
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
    machine_time = order["machine_time"].values[0]
    manual_time = order["manual_time"].values[0]
    work_time = machine_time - setuptime_material + setuptime_coil + manual_time
    return shift_model.compute_work_period(start_time, work_time)

def schedule_orders(
    shift_model,
    order_df,
    order_machine_mapping,
    priority_list,
    planning_period_start,
    planning_period_end,
):
    """Schedule the orders according to their priority to the available machines. Add planning information to dataframe.

    Args:
        order_df (_type_): pandas dataframe containing the orders
        order_machine_mapping (_type_): mapping from jobs to available machines
        priority_list (_type_): list of jobs ordered by priority
        planning_period_start (_type_): start of the planning period
        planning_period_end (_type_): end of the planning period

    Returns:
        _type_: pandas dataframe of the orders, where all orders within of planning period are planned.
    """
    # TODO consider end of planning period for jobs during scheduling
    # TODO include calendar and schichtmodell in computation
    # initiate machine jobs
    order_df["assigned_machine"] = -1
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
        assigned_machine = order_machine_mapping[job][0]
        if job["final_end"] > machine_endtime[assigned_machine]:
            machine_endtime[assigned_machine] = job["final_end"]
            machine_last_job[assigned_machine] = job
    for job in order_df.loc[order_df["status"] == JobStatus.PLANNED].iterrows():
        assigned_machine = order_machine_mapping[job][0]
        if job["planned_end"] > machine_endtime[assigned_machine]:
            machine_endtime[assigned_machine] = job["planned_end"]
            machine_last_job[assigned_machine] = job

    # iterate over prioritized jobs
    for job in priority_list:
        machine_tmp_id = ""
        machine_tmp_starttime = pd.Timestamp("NaT").to_pydatetime()
        machine_tmp_endtime = pd.Timestamp("NaT").to_pydatetime()
        # iterate over possible machines
        for machine in order_machine_mapping[job]:
            (machine_curr_starttime, machine_curr_endtime) = compute_job_period(
                shift_model, order_df, machine_endtime[machine], job, machine_last_job[machine]
            )
            if (
                pd.isnull(machine_tmp_endtime)
                or machine_curr_endtime < machine_tmp_endtime
            ):
                machine_tmp_id = machine
                machine_tmp_starttime = machine_curr_starttime
                machine_tmp_endtime = machine_curr_endtime

        order_df.loc[(order_df["job"] == job), "planned_start"] = machine_tmp_starttime
        order_df.loc[(order_df["job"] == job), "planned_end"] = machine_tmp_endtime
        order_df.loc[(order_df["job"] == job), "assigned_machine"] = machine_tmp_id
        machine_endtime[machine_tmp_id] = machine_tmp_endtime
        machine_last_job[machine_tmp_id] = job

    return order_df


# scheduling parameters
planning_period_start = datetime.datetime(2022, 5, 5, 8, 0, 0)  # 05.05.2020 8:00:00
planning_period_end = datetime.datetime(2022, 5, 12, 8, 0, 0)  # 12.05.22 8:00:00
priority_procedure = PriorityProcedure.FIRST_COME_FIRST_SERVE
shift_model_type = 'FLEX'

shift_model = ShiftModel(planning_period_start, shift_model_type)
order_df = get_orders()
order_df = filter_orders(order_df, planning_period_start, planning_period_end)
order_df = set_order_status(order_df)
order_machine_mapping = get_order_machine_mapping(order_df)
priority_list = compute_priority_list(order_df, priority_procedure)
order_df = schedule_orders(
    shift_model,
    order_df,
    order_machine_mapping,
    priority_list,
    planning_period_start,
    planning_period_end,
)
print(order_df[["job", "assigned_machine", "planned_start", "planned_end"]])
