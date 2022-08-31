import matplotlib.pyplot as plt
from adjustText import adjust_text
from IPython.display import display
import pandas as pd

import datetime

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
    bw = 0.3
    fig, axs = plt.subplots(figsize=(12, 0.7 * order_df.shape[0]))
    idx = 0
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
        y = x + datetime.timedelta(minutes=row["setup_time"])
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
            str(row["machine"]),
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
    machines = sorted([str(i) for i in order_df["machine"].unique()])

    plt.figure(figsize=(12, 5))
    texts = []
    for index, row in order_df.iterrows():
        idx = machines.index(str(row["machine"]))
        x = row["calculated_start"]
        y = row["calculated_end"]
        plt.fill_between(
            [x, y],
            [idx - bw / 2, idx - bw / 2],
            [idx + bw / 2, idx + bw / 2],
            color=ai_marketplace_blue_green,
            alpha=0.8,
        )
        plt.plot(
            [x, y, y, x, x],
            [idx - bw / 2, idx - bw / 2, idx + bw / 2, idx + bw / 2, idx - bw / 2],
            color="k",
            linewidth=1,
        )
        texts.append(
            plt.text(
                row["calculated_start"],
                idx + 0.25,
                "Job " + str(row["job"]),
                color="black",
                weight="bold",
                horizontalalignment="left",
                verticalalignment="bottom",
            )
        )
    plt.xlim(xlim)
    plt.ylim(-0.5, len(machines) - 0.5)
    plt.title("Machine Schedule")
    plt.yticks(range(len(machines)), machines)
    plt.ylabel("Machines")
    plt.grid(axis="x")
    # TODO readd function when problem with large database is solved
    # adjust_text(texts, only_move={'texts': 'y'})
    plt.show()
