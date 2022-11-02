# Own libraries
import visualization
import pyomomachsched
from shift import ShiftModel
import utility
import getordersdf

# Third party libraries
import datetime
import pandas as pd


# TODO: Rüstzeit erste Maschine?
# TODO: Startzeit current time?
def naive_termination(order_df, start, last_tool):
    """
    Calculates a simple termination from the given orders and returns it.

    Parameters
    ----------
    order_df: dataframe
        Orders in a dataframe containing the columns:
            machine, job, shift, order_release, duration_machine,
            setup_time
        Overwrites the values of following columns:
            calculated_start, calculated_end.
    start: datetime
        The start time of the naive termination calculation.
    last_tool: str
        The last tool name that has been used in the last job before the
        termination.

    Returns
    -------
    dataframe
        The orders with overwritten calculated_start and calculated_end.
    """
    machines = order_df["selected_machine"].astype(int).unique()
    company = order_df.attrs["company_name"]
    # Für jede Maschine
    for machine in machines:
        df_machine = order_df[order_df["selected_machine"].astype(int) == machine]
        timestamp = start
        # Entsprechend der Reihenfolge timestamps berechnen
        for index, row in df_machine.iterrows():
            order_num = row["job"]
            shift = row["shift"]

            # TODO: What about already running jobs? Or jobs that are finished?
            if timestamp < row["order_release"]:
                timestamp = row["order_release"]
            # Adjust timestamp to next shift start
            shifts = ShiftModel(company, shift, timestamp)
            timestamp = shifts.get_earliest_time(timestamp)

            order_df.loc[order_df["job"] == order_num, ["calculated_start"]] = timestamp
            tool = row["tool"]
            setup_time = row["setup_time"] if tool.casefold() != last_tool.casefold() else datetime.timedelta(0)
            order_df.loc[order_df["job"] == order_num, ["calculated_setup_time"]] = setup_time
            prod_time = row["duration_machine"]
            if isinstance(prod_time, datetime.timedelta):
                prod_time = prod_time.total_seconds() / 60
            if isinstance(setup_time, datetime.timedelta):
                setup_time = setup_time.total_seconds() / 60
            runtime = prod_time - 17 + setup_time + 2
            timestamp = utility.calculate_end_time(
                start=timestamp, duration=runtime, company=company, shift=shift
            )
            order_num = row["job"]
            order_df.loc[order_df["job"] == order_num, ["calculated_end"]] = timestamp
            last_tool = tool
    return order_df


def combine_orders(order_df, start):
    """
    Combines orders with the same item properties.
    """
    # TODO: FINISH THIS FUNCTION


if __name__ == "__main__":
    # Debugging
    df = getordersdf.get_westaflex_orders()
    df.drop(index=df.index[:180], axis=0, inplace=True)
    print(
        df[
            [
                "order_release",
                "machines",
                "selected_machine",
                "shift",
                "duration_machine",
                "calculated_start",
                "calculated_end",
                "setup_time",
            ]
        ]
    )
    df = naive_termination(df, datetime.datetime(2022, 2, 27, 6, 0, 0), "A0")
    print(
        df[
            [
                "order_release",
                "machines",
                "selected_machine",
                "shift",
                "duration_machine",
                "calculated_start",
                "calculated_end",
                "setup_time",
            ]
        ]
    )
    visualization.gantt(df)
    df = pyomomachsched.opt_schedule(df, datetime.datetime(2022, 1, 2, 0, 0, 0))
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(
            df[
                [
                    "order_release",
                    "tool",
                    "machines",
                    "selected_machine",
                    "shift",
                    "duration_machine",
                    "setup_time",
                    "calculated_start",
                    "calculated_end",
                ]
            ]
        )
    df.to_pickle("./pyomo_df.pkl")
    df.to_excel("./pyomo_df.xlsx")
    df.to_csv("./pyomo_df.csv")
    visualization.gantt(df)
