"""Provides helper functions for datetime and shift handling.
"""
# Own libraries
from shift import ShiftModel

# Third party libraries
import datetime
import pandas as pd


def calculate_end_time(start: datetime.datetime,
                       duration: int,
                       company: str,
                       shift: str) -> datetime.datetime:
    """
    Calculates the time a job gets finished based on the given duration.

    Takes a start and a duration, and considers company holidays as well as
    operating shifts, to calculate the end time of the finished job and
    returns it.

    Parameters
    ----------
    start : datetime.datetime
        The start time of the job.
    duration : int
        The duration of the job in minutes.
    company : str
        The company name from which to take the shift model.
    shift : str
        The shift model determines which hours are available for work.
        Possible shift models are:
            Flex, FlexS, Flex+S, W01S1, W01S3, W01YL, W011

    Returns
    -------
    datetime.datetime
        The end time of the job.
    """
    if isinstance(start, pd.Timestamp):
        start = start.to_pydatetime()
    elif isinstance(start, datetime.datetime):
        pass
    else:
        raise ValueError(
            'start parameter needs to be of type datetime.datetime or pandas.Timestamp')

    shifts = ShiftModel(company, shift, start)
    # Add the duration of the job to the current shift time
    current_shift_time = shifts.add_time(datetime.timedelta(minutes=duration))

    return current_shift_time


def convert_str_to_datetime(date: str) -> datetime.datetime:
    """
    Converts string format dd.mm.yyyy to datetime object
    """
    if isinstance(date, datetime.datetime):
        return date
    if not isinstance(date, str):
        return datetime.datetime(0, 0, 0)
    if not date or date.lower() == 'nan':
        return datetime.datetime(0, 0, 0)
    if not date.count('.') == 2 or len(date) != 10:
        raise ValueError(f'{date} not expected format dd.mm.yyyy')
    # Turn date around to yyyy-mm-dd first
    date = date.split('.')
    if len(date[0]) == 4:
        # In format yyyy.mm.dd, so reverse list
        date.reverse()
    swapped_date = date[2] + '-' + date[1] + '-' + date[0]
    return datetime.datetime.fromisoformat(swapped_date)
