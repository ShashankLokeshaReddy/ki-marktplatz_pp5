import datetime


class ShiftModel:
    """Add description
    """

    def __init__(self, current_shift_time, shift_model):
        # TODO: This is just a temporary solution, the values should be read from somewhere else
        # TODO: Move this data structure somewhere else, so it does not have to be loaded with each instantiation
        # Time intervals of each shift model. 0:=Monday, 1:=Tuesday, and so on.
        self.shifts = {'FLEX': {0: [[datetime.time(6, 0), datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(15, 00)]],
                                1: [[datetime.time(6, 0), datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(15, 00)]],
                                2: [[datetime.time(6, 0), datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(15, 00)]],
                                3: [[datetime.time(6, 0), datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(15, 00)]],
                                4: [[datetime.time(6, 0), datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(13, 45)]],
                                5: [[datetime.time(0, 0), datetime.time(0, 0)]],
                                6: [[datetime.time(0, 0), datetime.time(0, 0)]]},
                       'FLEXS': {0: [[datetime.time(15, 0), datetime.time(19, 0)],
                                     [datetime.time(19, 30), datetime.time(23, 45)]],
                                 1: [[datetime.time(15, 0), datetime.time(19, 0)],
                                     [datetime.time(19, 30), datetime.time(23, 45)]],
                                 2: [[datetime.time(15, 0), datetime.time(19, 0)],
                                     [datetime.time(19, 30), datetime.time(23, 45)]],
                                 3: [[datetime.time(15, 0), datetime.time(19, 0)],
                                     [datetime.time(19, 30), datetime.time(23, 45)]],
                                 4: [[datetime.time(14, 0), datetime.time(19, 0)],
                                     [datetime.time(19, 30), datetime.time(23, 30)]],
                                 5: [[datetime.time(0, 0), datetime.time(0, 0)]],
                                 6: [[datetime.time(0, 0), datetime.time(0, 0)]]},
                       'FLEX+S': {0: [[datetime.time(6, 0), datetime.time(12, 30)],
                                      [datetime.time(13, 0),
                                       datetime.time(15, 0)],
                                      [datetime.time(15, 0),
                                       datetime.time(19, 0)],
                                      [datetime.time(19, 30), datetime.time(23, 45)]],
                                  1: [[datetime.time(6, 0), datetime.time(12, 30)],
                                      [datetime.time(13, 0),
                                       datetime.time(15, 0)],
                                      [datetime.time(15, 0),
                                      datetime.time(19, 0)],
                                      [datetime.time(19, 30), datetime.time(23, 45)]],
                                  2: [[datetime.time(6, 0), datetime.time(12, 30)],
                                      [datetime.time(13, 0),
                                       datetime.time(15, 0)],
                                      [datetime.time(15, 0),
                                      datetime.time(19, 0)],
                                      [datetime.time(19, 30), datetime.time(23, 45)]],
                                  3: [[datetime.time(6, 0), datetime.time(12, 30)],
                                      [datetime.time(13, 0),
                                       datetime.time(15, 0)],
                                      [datetime.time(15, 0),
                                      datetime.time(19, 0)],
                                      [datetime.time(19, 30), datetime.time(23, 45)]],
                                  4: [[datetime.time(6, 0), datetime.time(12, 30)],
                                      [datetime.time(13, 0),
                                       datetime.time(13, 45)],
                                      [datetime.time(14, 0),
                                      datetime.time(19, 0)],
                                      [datetime.time(19, 30), datetime.time(23, 30)]],
                                  5: [[datetime.time(0, 0), datetime.time(0, 0)]],
                                  6: [[datetime.time(0, 0), datetime.time(0, 0)]]},
                       'W01S1': {0: [[datetime.time(6, 0), datetime.time(14, 5)],
                                     [datetime.time(14, 10), datetime.time(22, 15)]],
                                 1: [[datetime.time(6, 0), datetime.time(14, 5)],
                                     [datetime.time(14, 10), datetime.time(22, 15)]],
                                 2: [[datetime.time(6, 0), datetime.time(14, 5)],
                                     [datetime.time(14, 10), datetime.time(22, 15)]],
                                 3: [[datetime.time(6, 0), datetime.time(14, 5)],
                                     [datetime.time(14, 10), datetime.time(22, 15)]],
                                 4: [[datetime.time(6, 0), datetime.time(11, 25)],
                                     [datetime.time(11, 30), datetime.time(16, 45)]],
                                 5: [[datetime.time(0, 0), datetime.time(0, 0)]],
                                 6: [[datetime.time(0, 0), datetime.time(0, 0)]]},
                       'W01S3': {0: [[datetime.time(6, 0), datetime.time(23, 55)]],
                                 1: [[datetime.time(0, 0), datetime.time(23, 55)]],
                                 2: [[datetime.time(0, 0), datetime.time(23, 55)]],
                                 3: [[datetime.time(0, 0), datetime.time(23, 55)]],
                                 4: [[datetime.time(0, 0), datetime.time(23, 55)]],
                                 5: [[datetime.time(0, 0), datetime.time(6, 15)]],
                                 6: [[datetime.time(0, 0), datetime.time(0, 0)]]},
                       'W01YL': {0: [[datetime.time(6, 0), datetime.time(21, 45)]],
                                 1: [[datetime.time(6, 0), datetime.time(21, 45)]],
                                 2: [[datetime.time(6, 0), datetime.time(21, 45)]],
                                 3: [[datetime.time(6, 0), datetime.time(21, 45)]],
                                 4: [[datetime.time(6, 0), datetime.time(21, 45)]],
                                 5: [[datetime.time(0, 0), datetime.time(0, 0)]],
                                 6: [[datetime.time(0, 0), datetime.time(0, 0)]]},
                       'W011': {0: [[datetime.time(6, 0), datetime.time(9, 0)],
                                    [datetime.time(9, 15),
                                     datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(17, 30)]],
                                1: [[datetime.time(6, 0), datetime.time(9, 0)],
                                    [datetime.time(9, 15),
                                    datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(17, 30)]],
                                2: [[datetime.time(6, 0), datetime.time(9, 0)],
                                    [datetime.time(9, 15),
                                    datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(17, 30)]],
                                3: [[datetime.time(6, 0), datetime.time(9, 0)],
                                    [datetime.time(9, 15),
                                    datetime.time(12, 30)],
                                    [datetime.time(13, 0), datetime.time(17, 30)]],
                                4: [[datetime.time(6, 0), datetime.time(9, 0)],
                                    [datetime.time(9, 15), datetime.time(13, 0)]],
                                5: [[datetime.time(0, 0), datetime.time(0, 0)]],
                                6: [[datetime.time(0, 0), datetime.time(0, 0)]]}
                       }
        self.company_holidays = [datetime.date(2022, 1, 1),
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
        if shift_model not in self.get_shift_names():
            raise ValueError(
                f'Object instantiation failed, since "{shift_model}" is not' +
                ' a supported shift model.')
        self.shift_model = shift_model
        # Set current shift time to the first hour of the next shift day if it
        # is outside the working hours
        self.current_shift_time = self.get_earliest_time(current_shift_time)

    def float_to_datetime(self, minutes: float) -> datetime:
        min = int(minutes)
        h = int(min/60)
        sec = int((minutes - int(minutes)) * 60)
        min -= 60 * h
        res = datetime.time(h, min, sec)
        return res

    def compute_work_period(self, start_time, work_time: float) -> datetime:
        """_summary_

        Args:
            start_time (_type_): _description_
            work_time (float): Time for job work time given in minutes as float

        Returns:
            datetime: _description_
        """
        # Compute earliest actual start time within shift model
        period_start = self.get_earliest_time(start_time)
        current_datetime = period_start #  TODO deep copy?
        # convert work_time to seconds
        work_time = int(work_time) * 60 + round((work_time - int(work_time)) * 60)

        while work_time:
            day_shift = self.shifts[self.shift_model][current_datetime.weekday()]
            for interval in day_shift:
                # Correct current time to be in an interval of the shift model
                current_datetime = self.get_earliest_time(current_datetime)

                # Check if current time is in the current interval
                if interval[0] <= current_datetime.time() and current_datetime.time() < interval[1]:  
                    # Compute remaining time in the interval 
                    tmp_end = datetime.datetime.combine(datetime.date.today(), interval[1])
                    tmp_start = datetime.datetime.combine(datetime.date.today(), current_datetime.time())
                    interval_delta = tmp_end - tmp_start

                    if work_time >= interval_delta.seconds:
                        current_datetime = current_datetime.replace(hour=interval[1].hour, minute=interval[1].minute)
                        work_time -= interval_delta.seconds
                    else:
                        current_datetime = current_datetime + datetime.timedelta(seconds=work_time)
                        work_time = 0

        return (period_start, current_datetime)

    def add_time(self, working_time: int) -> datetime:
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

        # Check if current time is actually during a shift timeframe
        self.current_shift_time = self.get_earliest_time(
            self.current_shift_time)

        while working_time:
            day_shift = self.shifts[self.shift_model][self.current_shift_time.weekday(
            )]
            for interval in day_shift:
                # Check if current time is actually during a shift timeframe
                self.current_shift_time = self.get_earliest_time(
                    self.current_shift_time)
                # Minutes during this interval
                interval_minutes = (datetime.datetime.combine(self.current_shift_time.date(), interval[1]) -
                                    self.current_shift_time).total_seconds() / 60
                if working_time >= interval_minutes:
                    # Whole interval can be worked through
                    working_time -= interval_minutes
                    self.current_shift_time = self.current_shift_time.replace(
                        hour=interval[1].hour,
                        minute=interval[1].minute)
                else:
                    # Work stops during current interval
                    self.current_shift_time += datetime.timedelta(
                        minutes=working_time)
                    working_time = 0
                    break
        return self.current_shift_time

    def get_shift_names(self):
        """Returns the names of all available shifts as list of strings.
        """
        return list(self.shifts.keys())

    def get_holidays(self):
        """Returns the holidays as a list.
        """
        return self.company_holidays

    def get_earliest_time(self, start: datetime) -> datetime:
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
            start = start + datetime.timedelta(days=1)
        weekday = start.weekday()
        # Iterate through all time intervals of the day and check whether
        # the start time lies in one of those intervals
        for interval in self.shifts[self.shift_model][weekday]:
            if interval[0] <= start.time() < interval[1]:
                # The start time lies between the working hours of the shift
                return start
            elif start.time() < interval[0]:
                # The start time lies before the shift begins,
                # set to shift beginning
                return start.replace(hour=interval[0].hour,
                                     minute=interval[0].minute)
        # The start time does not lie in the working hours of the shift day
        # return the next available day
        # TODO: Check end of year, to jump to next year
        temp_interval = self.shifts[self.shift_model][(weekday + 1) % 6][0]
        day_skips = 1
        if temp_interval[1] == datetime.time(0, 0) and weekday == 5:
            # Saturday, no hours for this shift, get monday
            day_skips = 2
        return datetime.datetime(start.year, start.month, start.day,
                                 temp_interval[0].hour,
                                 temp_interval[0].minute) + \
            datetime.timedelta(days=day_skips)
