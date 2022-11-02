import matplotlib.pyplot as plt
from adjustText import adjust_text
import pandas as pd

import datetime
from shift import ShiftModel

# Colors
ai_marketplace_red = "#d50c2f"
ai_marketplace_red_light = "#f7cfd6"
ai_marketplace_blue_green = "#006C7D"
ai_marketplace_green = "#A9C23F"
ai_marketplace_orange = "#FF9E1B"


# TODO: Temporary solution
company_holidays = [
    datetime.date(2022, 1, 1),
    datetime.date(2022, 4, 15),
    datetime.date(2022, 4, 16),
    datetime.date(2022, 4, 17),
    datetime.date(2022, 4, 18),
    datetime.date(2022, 5, 1),
    datetime.date(2022, 5, 26),
    datetime.date(2022, 5, 27),
    datetime.date(2022, 5, 28),
    datetime.date(2022, 6, 5),
    datetime.date(2022, 6, 6),
    datetime.date(2022, 6, 16),
    datetime.date(2022, 6, 17),
    datetime.date(2022, 6, 18),
    datetime.date(2022, 10, 3),
    datetime.date(2022, 10, 31),
    datetime.date(2022, 11, 1),
    datetime.date(2022, 12, 24),
    datetime.date(2022, 12, 25),
    datetime.date(2022, 12, 26),
    datetime.date(2022, 12, 27),
    datetime.date(2022, 12, 28),
    datetime.date(2022, 12, 29),
    datetime.date(2022, 12, 30),
    datetime.date(2022, 12, 31),
]


def gantt(order_df):
    """Visualize the order table as a Gantt chart as a job and a machine chart."""
    # TODO: Seperate into smaller functions
    bw = 0.3
    fig, axs = plt.subplots(figsize=(12, 0.7 * order_df.shape[0]))
    idx = 0
    # Shift downtimes as gray bars
    shift_name = order_df.iloc[-1]["shift"]
    # shift_name = 'W01S3'
    axs.text(
        0.05,
        1.01,
        f"shift: {shift_name}",
        verticalalignment="bottom",
        horizontalalignment="left",
        transform=axs.transAxes,
        color="black",
        fontsize=15,
    )
    # TODO: temporary solution, company name needs to be in the order_df
    company = order_df.attrs["company_name"]
    shift = ShiftModel(company, shift_name)
    shift_intervals = []
    if (
        order_df["calculated_end"].max().date()
        < order_df["deadline"].max().to_pydatetime().date()
    ):
        end = order_df["deadline"].max().to_pydatetime().date()
    else:
        end = order_df["calculated_end"].max().date()
    for day in (
        pd.date_range(
            start=order_df["order_release"].min().to_pydatetime().date(), end=end
        )
        .strftime("%Y-%m-%d")
        .tolist()
    ):
        day = datetime.datetime.fromisoformat(day)
        day_shift = shift.shifts.loc[
                (shift.shifts["shift"] == shift_name)
                & (shift.shifts["weekday"] == day.weekday()),
                "interval0":"interval5",
            ].values[0]
        for interval in day_shift[day_shift != None]:
            x = datetime.datetime.combine(day, interval[0])
            y = datetime.datetime.combine(day, interval[1])
            shift_intervals.append((x, y))
        if day in shift.company_holidays:
            x = day
            y = day + datetime.timedelta(days=1)
            axs.axvspan(x, y, color="gray", alpha=0.3)
    for index, interval in enumerate(shift_intervals):
        if index < len(shift_intervals) - 1:
            axs.axvspan(
                interval[1], shift_intervals[index + 1][0], color="gray", alpha=0.3
            )

    for index, row in order_df.iterrows():
        x = row["order_release"]
        y = row["deadline"]
        axs.fill_between(
            [x, y],
            [idx - bw / 4, idx - bw / 4],
            [idx + bw / 4, idx + bw / 4],
            color=ai_marketplace_green,
            alpha=0.6,
            linewidth=0,
            edgecolor="black",
        )
        x = row["calculated_start"]
        y = row["calculated_end"]
        axs.fill_between(
            [x, y],
            [idx - bw / 2, idx - bw / 2],
            [idx + bw / 2, idx + bw / 2],
            color=ai_marketplace_blue_green,
            alpha=0.8,
            linewidth=0,
        )
        # Color missed deadline in red
        if y > row["deadline"]:
            x_missed = row["calculated_end"]
            y_missed = row["deadline"]
            axs.fill_between(
                [x_missed, y_missed],
                [idx - bw / 2, idx - bw / 2],
                [idx + bw / 2, idx + bw / 2],
                color="red",
                alpha=0.8,
                linewidth=0,
            )
        # Setup time in yellow
        calculated_setup_time = row["calculated_setup_time"]
        if not isinstance(calculated_setup_time, datetime.timedelta):
            calculated_setup_time = datetime.timedelta(minutes=calculated_setup_time)
        y = x + calculated_setup_time
        axs.fill_between(
            [x, y],
            [idx - bw / 2, idx - bw / 2],
            [idx + bw / 2, idx + bw / 2],
            color=ai_marketplace_orange,
            alpha=1,
            linewidth=0,
        )
        # Black bars at beginning and end
        # plt.plot([x, y, y, x, x], [idx - bw, idx - bw,
        #                           idx + bw, idx + bw, idx - bw], color='k')
        # Machine number
        axs.text(
            row["calculated_end"],
            idx,
            str(row["selected_machine"]),
            color="black",
            weight="bold",
            horizontalalignment="left",
            verticalalignment="center",
        )
        idx += 1

    axs.set_ylim(-0.5, idx - 0.5)
    axs.set_title("Job Schedule")
    axs.set_xlabel("Time")
    axs.set_ylabel("Jobs")
    axs.set_yticks(range(len(order_df.index)), order_df.loc[:, "job"])
    # axs.set_xticks()
    axs.grid(axis="x")
    axs.set_axisbelow(True)
    xlim = axs.set_xlim(order_df["order_release"].min(), order_df["deadline"].max())
    # Highlight holidays
    for holiday in company_holidays:
        plt.axvspan(
            holiday,
            holiday + datetime.timedelta(days=1),
            facecolor="gray",
            edgecolor="none",
            alpha=0.5,
        )

    # Machine plot
    # TODO: List all machines, even when not used at all
    machines = sorted([str(i) for i in order_df["selected_machine"].unique()])
    # remove duplicates
    machines = list(dict.fromkeys(machines))

    fig, axs = plt.subplots(figsize=(12, 5))
    # Shift downtimes as gray bars
    # TODO: Put into own function
    shift = ShiftModel(company, shift_name)
    shift_intervals = []
    for day in (
        pd.date_range(
            start=order_df["order_release"].min().to_pydatetime().date(), end=end
        )
        .strftime("%Y-%m-%d")
        .tolist()
    ):
        day = datetime.datetime.fromisoformat(day)
        day_shift = shift.shifts.loc[
                (shift.shifts["shift"] == shift_name)
                & (shift.shifts["weekday"] == day.weekday()),
                "interval0":"interval5",
            ].values[0]
        for interval in day_shift[day_shift != None]:
            x = datetime.datetime.combine(day, interval[0])
            y = datetime.datetime.combine(day, interval[1])
            shift_intervals.append((x, y))
        if day in shift.company_holidays:
            x = day
            y = day + datetime.timedelta(days=1)
            axs.axvspan(x, y, color="gray", alpha=0.3)
    for index, interval in enumerate(shift_intervals):
        if index < len(shift_intervals) - 1:
            axs.axvspan(
                interval[1], shift_intervals[index + 1][0], color="gray", alpha=0.3
            )

    texts = []
    for index, row in order_df.iterrows():
        idx = machines.index(str(row["selected_machine"]))
        x = row["calculated_start"]
        y = row["calculated_end"]
        axs.fill_between(
            [x, y],
            [idx - bw / 2, idx - bw / 2],
            [idx + bw / 2, idx + bw / 2],
            color=ai_marketplace_blue_green,
            alpha=0.8,
        )
        axs.plot(
            [x, y, y, x, x],
            [idx - bw / 2, idx - bw / 2, idx + bw / 2, idx + bw / 2, idx - bw / 2],
            color="k",
            linewidth=1,
        )
        texts.append(
            axs.text(
                row["calculated_start"],
                idx + 0.25,
                "Job " + str(row["job"]),
                color="black",
                weight="bold",
                horizontalalignment="left",
                verticalalignment="bottom",
            )
        )
    axs.set_xlim(xlim)
    axs.set_ylim(-0.5, len(machines) - 0.5)
    axs.set_title("Machine Schedule")
    axs.set_yticks(range(len(machines)), machines)
    axs.set_ylabel("Machines")
    axs.grid(axis="x")
    adjust_text(texts, only_move={"texts": "y"})
    plt.show()
