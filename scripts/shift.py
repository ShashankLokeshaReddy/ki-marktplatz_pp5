# TODO: take into consideration when end time reaches next year

import datetime
import pathlib
import os
import pandas as pd


# Current script directory
script_directory = pathlib.Path(__file__).parent.resolve()
# Default path of the shifts tables
default_shifts_path = os.path.join(script_directory, '..', 'data')


class ShiftModel:
    """Handles shift times and holidays of a company.
    """

    def __init__(self, name, shift_name, current_shift_time=datetime.datetime(2022, 1, 1)):
        try:
            self.shifts = self.read_shifts_csv(name)
        except OSError as exc:
            raise OSError(f'A shifts table for {name} does not exist') from exc
        try:
            self.company_holidays = self.read_holidays_csv(name)
        except OSError as exc:
            raise OSError(
                f'A holidays table for {name} does not exist') from exc
        if not self.shifts['shift'].str.contains(shift_name).any():
            raise ValueError(
                f'Object instantiation failed, since "{shift_name}" is not' +
                ' a supported shift model.')
        self.shift_name = shift_name.upper()
        # Set current shift time to the first hour of the next shift day if it
        # is outside the working hours
        self.current_shift_time = self.get_earliest_time(current_shift_time)

    def read_shifts_csv(self, name: str) -> pd.DataFrame:
        """Reads the csv containing the shift times and returns it as dataframe

        Args:
            name (str): the name of the csv file to read
        """
        name.replace('shifts_', '')
        name.replace('.csv', '')

        def str_interval_to_datetime_interval(interval):
            # transforms the HH:MM-HH:MM string interval into a datetime interval
            if isinstance(interval, str):
                return [datetime.datetime.strptime(
                        str(interval).split('-')[0], '%H:%M').time(),
                        datetime.datetime.strptime(str(interval).split('-')[1], '%H:%M').time()]
            else:
                return None

        csv_path = os.path.join(default_shifts_path, 'shifts_' + name + '.csv')
        if os.path.exists(csv_path):
            shift_df = pd.read_csv(csv_path)
            for i in range(6):
                shift_df.loc[:, 'interval' + str(i)] = shift_df['interval' +
                                                                str(i)].apply(str_interval_to_datetime_interval)
            return shift_df

        raise OSError(f"Following path was not found: {csv_path}.")

    def read_holidays_csv(self, name: str) -> list:
        """Reads the csv containing the company holidays and returns it as list

        Args:
            name (str): the name of the csv file to read
        """
        name.replace('holidays_', '')
        name.replace('.csv', '')

        csv_path = os.path.join(default_shifts_path,
                                'holidays_' + name + '.csv')
        if os.path.exists(csv_path):
            holidays_df = pd.read_csv(csv_path)
            # Transform all strings of the table into datetime objects
            return holidays_df['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d').date()).to_list()
        raise OSError(f"Following path was not found: {csv_path}.")

    def compute_work_period(self, start_time, work_time: float):
        """Compute the work period based on the shift model for a given start datetime and a work time.
        Returns a tuple of the working period begin and end as datetime.

        Args:
            start_time (_type_): _description_
            work_time (float): Time for job work time given in minutes as float
        """
        # Compute earliest actual start time within shift model
        period_start = self.get_earliest_time(start_time)
        current_datetime = period_start
        # convert work_time to seconds
        work_time = int(work_time) * 60 + \
            round((work_time - int(work_time)) * 60)

        while work_time:
            #day_shift = self.shifts[self.shift_name][current_datetime.weekday()]
            day_shift = self.shifts.loc[(self.shifts['shift'] == self.shift_name) &
                                        (self.shifts['weekday'] == current_datetime.weekday()), 'interval0':'interval5'].values[0]
            for interval in day_shift[day_shift != None]:
                # Correct current time to be in an interval of the shift model
                current_datetime = self.get_earliest_time(current_datetime)

                # Check if current time is in the current interval
                if (
                    interval[0] <= current_datetime.time()
                    and current_datetime.time() < interval[1]
                ):
                    # Compute remaining time in the interval
                    tmp_end = datetime.datetime.combine(
                        datetime.date.today(), interval[1]
                    )
                    tmp_start = datetime.datetime.combine(
                        datetime.date.today(), current_datetime.time()
                    )
                    interval_delta = tmp_end - tmp_start

                    if work_time >= interval_delta.seconds:
                        current_datetime = current_datetime.replace(
                            hour=interval[1].hour, minute=interval[1].minute
                        )
                        work_time -= interval_delta.seconds
                    else:
                        current_datetime = current_datetime + datetime.timedelta(
                            seconds=work_time
                        )
                        work_time = 0

        return (period_start, current_datetime)

    def count_time(self, start: datetime.datetime, end: datetime.datetime) -> int:
        """Counts the amount of seconds of the shift in the given interval
        and returns it.

        Parameters
        ----------
        start : datetime.datetime
            Start of the interval where counting starts.
        end : datetime.datetime
            End of the interval where counting ends.

        Returns
        -------
        int
            Amount of seconds the shift has during the given interval.
        """
        accumulated_seconds = 0
        current_time = start
        # Set end time to a valid time of the shift model
        end = self.get_earliest_time(end)
        while current_time < end:
            # Check if current time is actually during a shift timeframe
            current_time = self.get_earliest_time(
                current_time)
            # day_shift = self.shifts[self.shift_name][current_time.weekday()]
            day_shift = self.shifts.loc[(self.shifts['shift'] == self.shift_name) &
                                        (self.shifts['weekday'] == current_time.weekday()), 'interval0':'interval5'].values[0]
            for interval in day_shift[day_shift != None]:
                shift_end = datetime.datetime.combine(current_time.date(),
                                                      interval[1])
                if current_time > shift_end:
                    # Current shift time does not lie in current interval
                    continue

                if end >= shift_end:
                    # Whole interval can be worked through
                    # Add all seconds during this interval
                    accumulated_seconds += (shift_end -
                                            current_time).total_seconds()
                    # Set current time to end of current interval
                    current_time = current_time.replace(
                        hour=interval[1].hour,
                        minute=interval[1].minute,
                        second=interval[1].second)
                else:
                    # Work stops during current interval
                    accumulated_seconds += (end - current_time).total_seconds()
                    current_time = end
                    break
                # Check if current time is actually during a shift timeframe
                current_time = self.get_earliest_time(current_time)
        return accumulated_seconds

    def add_time(self, working_time: int) -> datetime.datetime:
        """Add working time to the current_shift_time and return the new time.

        Parameters
        ----------
        working_time : int
            Time that progresses the shift model time in minutes.

        Returns
        -------
        datetime.datetime
        """
        # TODO: Should the working time be float (e.g. 3.4 minutes)?
        # Then it needs to be converted to seconds
        if isinstance(working_time, datetime.timedelta):
            working_time = working_time.total_seconds() / 60

        # Set current time to a valid shift timeframe
        self.current_shift_time = self.get_earliest_time(
            self.current_shift_time)

        while working_time:
            #day_shift = self.shifts[self.shift_name][self.current_shift_time.weekday()]
            day_shift = self.shifts.loc[(self.shifts['shift'] == self.shift_name) &
                                        (self.shifts['weekday'] == self.current_shift_time.weekday()), 'interval0':'interval5'].values[0]
            for interval in day_shift[day_shift != None]:
                shift_end = datetime.datetime.combine(self.current_shift_time.date(),
                                                      interval[1])
                if self.current_shift_time > shift_end:
                    # Current shift time does not lie in current interval
                    continue
                # Minutes during this interval
                interval_minutes = (shift_end -
                                    self.current_shift_time).total_seconds() / 60
                if working_time >= interval_minutes:
                    # Whole interval can be worked through
                    working_time -= interval_minutes
                    # Set current time to end of current interval
                    self.current_shift_time = self.current_shift_time.replace(
                        hour=interval[1].hour,
                        minute=interval[1].minute,
                        second=interval[1].second)
                else:
                    # Work stops during current interval
                    self.current_shift_time += datetime.timedelta(
                        minutes=working_time)
                    working_time = 0
                    break
                # Check if current time is actually during a shift timeframe
                self.current_shift_time = self.get_earliest_time(
                    self.current_shift_time)
        self.current_shift_time = self.get_earliest_time(
            self.current_shift_time)
        return self.current_shift_time

    def get_shift_names(self):
        """Returns the names of all available shifts as set of strings.
        """
        return set(self.shifts['shift'].to_list())

    def get_holidays(self):
        """Returns the holidays as a list.
        """
        return self.company_holidays

    def get_earliest_time(self, start: datetime.datetime) -> datetime.datetime:
        """Returns the earliest time a shift can start after the given time.

        Parameters
        ----------
        start : datetime.datetime
            Time that needs to be adjusted to the next shift start if needed.

        Returns
        -------
        datetime.datetime
            Adjusted time to the next shift start if the input was not in any
            shift timeframes
        """
        # Skip as many days as there are holidays
        while start.date() in self.company_holidays:
            start = start.replace(hour=0, minute=0) + \
                datetime.timedelta(days=1)
        weekday = start.weekday()
        # Iterate through all time intervals of the day and check whether
        # the start time lies in one of those intervals
        day_shift = self.shifts.loc[(self.shifts['shift'] == self.shift_name) &
                                    (self.shifts['weekday'] == weekday), 'interval0':'interval5'].values[0]
        for interval in day_shift[day_shift != None]:
            if interval[0] <= start.time() < interval[1]:
                # The start time lies between the working hours of the shift
                return start
            elif start.time() < interval[0]:
                # The start time lies before the shift begins,
                # set to shift beginning
                return start.replace(hour=interval[0].hour,
                                     minute=interval[0].minute,
                                     second=interval[0].second)
        # The start time does not lie in the working hours of the shift day
        # return the next available day
        # TODO: Check end of year, to jump to next year
        temp_interval = self.shifts.loc[(self.shifts['shift'] == self.shift_name) &
                                        (self.shifts['weekday'] == (weekday + 1) % 6), 'interval0'].values[0]
        start = datetime.datetime(start.year, start.month, start.day,
                                  temp_interval[0].hour,
                                  temp_interval[0].minute,
                                  temp_interval[0].second) + \
            datetime.timedelta(days=1)
        # Check again if the new start time lies in an actual shift interval
        return self.get_earliest_time(start)


# tests
if __name__ == "__main__":
    shift = ShiftModel('westaflex', 'FLEX', datetime.datetime(2022, 6, 3))
    print(
        f"2 hours between 2 days test:\nExpected: {7200.0}, actual: {shift.count_time(datetime.datetime(2022, 6, 7, 14, 0, 0), datetime.datetime(2022, 6, 8, 7, 0, 0))}")
    print(
        f"Hours on weekend test:\nExpected: {0.0}, actual: {shift.count_time(datetime.datetime(2022, 6, 4, 14, 0, 0), datetime.datetime(2022, 6, 5, 7, 0, 0))}")
    print(
        f"Hours over holiday test:\nExpected: {3600.0}, actual: {shift.count_time(datetime.datetime(2022, 6, 3, 14, 0, 0), datetime.datetime(2022, 6, 7, 7, 0, 0))}")
    print(
        f"Skip holidays test:\nExpected: {7200.0}, actual: {shift.count_time(datetime.datetime(2022, 6, 15, 14, 0, 0), datetime.datetime(2022, 6, 20, 7, 0, 0))}")
    print(
        f"Get earliest time test:\nExpected: 2022-06-07 06:00:00, actual: {shift.get_earliest_time(datetime.datetime(2022, 6, 7))}")
    shift = ShiftModel('westaflex', 'W01S3', datetime.datetime(2022, 3, 9))
    time_in_shift = shift.count_time(datetime.datetime(
        2022, 3, 9), datetime.datetime(2022, 3, 21))
    print(
        f"Time in shift calculation test:\nExpected: 2022-03-21, actual: {shift.add_time(time_in_shift / 60)}")

    # shifts_df = shift.read_shifts_csv('westaflex')
    # shifts_df.to_csv('shifts_westaflex.csv')
    # print(shifts_df[['shift', 'weekday', 'interval0', 'interval1']])
