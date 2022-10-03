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
        if shift_model.lower() not in [i.lower() for i in self.get_shift_names()]:
            raise ValueError(
                f'Object instantiation failed, since "{shift_model}" is not' +
                ' a supported shift model.')
        self.shift_model = shift_model.upper()
        # Set current shift time to the first hour of the next shift day if it
        # is outside the working hours
        self.current_shift_time = self.get_earliest_time(current_shift_time)

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
            day_shift = self.shifts[self.shift_model][current_time.weekday()]
            for interval in day_shift:
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
            day_shift = self.shifts[self.shift_model][self.current_shift_time.weekday(
            )]
            for interval in day_shift:
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
        """Returns the names of all available shifts as list of strings.
        """
        return list(self.shifts.keys())

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
        for interval in self.shifts[self.shift_model][weekday]:
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
        temp_interval = self.shifts[self.shift_model][(weekday + 1) % 6][0]
        start = datetime.datetime(start.year, start.month, start.day,
                                  temp_interval[0].hour,
                                  temp_interval[0].minute,
                                  temp_interval[0].second) + \
            datetime.timedelta(days=1)
        # Check again if the new start time lies in an actual shift interval
        return self.get_earliest_time(start)


# Unit tests
if __name__ == "__main__":
    shift = ShiftModel(datetime.datetime(2022, 6, 3), 'FLEX')
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
    shift = ShiftModel(datetime.datetime(2022, 3, 9), 'W01S3')
    time_in_shift = shift.count_time(datetime.datetime(
        2022, 3, 9), datetime.datetime(2022, 3, 21))
    print(
        f"Time in shift calculation test:\nExpected: 2022-03-21, actual: {shift.add_time(time_in_shift / 60)}")
