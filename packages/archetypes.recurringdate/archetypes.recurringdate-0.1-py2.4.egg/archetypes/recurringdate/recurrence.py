from dateutil import rrule
from DateTime import DateTime
from p4a.common.dtutils import DT2dt

class RecurringData(object):
    """Stores all the fields from the recurring widget."""
    enabled = False
    start_time = ''
    end_time = ''
    duration = ''
    frequency = 3 # 2, 1, 0
    daily_interval = 'day' # 'weekday'
    daily_interval_number = 1
    weekly_interval = () # (0, 1, 2, 3, 4, 5, 6)
    weekly_interval_number = 1
    monthly_interval = 'dayofmonth' # 'dayofweek'
    monthly_interval_day = 1
    monthly_interval_number1 = 1
    monthly_interval_number2 = 1
    monthly_ordinal_week = 1
    monthly_weekday = 0
    yearly_interval = 'dayofmonth' # 'dayofweek'
    yearly_month1 = 1
    yearly_month2 = 1
    yearly_interval_day = 1
    yearly_ordinal_week = 1
    yearly_weekday = 0
    range_name = 'ever' # 'count', 'until'
    range_count = 10
    start_date = ''
    end_date = ''

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def getRecurrenceRule(self):
        if not self.enabled:
            return None

        dtstart = ('%s %s' % (self.start_date, self.start_time)).strip()
        if not dtstart:
            return None

        dtstart = DT2dt(DateTime(dtstart))
        params = dict(
            dtstart=dtstart,
            #wkst=None,
            #byyearday=None,
            #byeaster=None,
            #byweekno=None,
            #byhour=None,
            #byminute=None,
            #bysecond=None,
            #cache=False
        )

        # byweekday
        if self.frequency == rrule.DAILY and self.daily_interval == 'weekday':
            params['byweekday'] = range(5)
        elif self.frequency == rrule.WEEKLY:
            days = [int(day) for day in self.weekly_interval]
            if not days:
                days = [dtstart.weekday()]
            params['byweekday'] = days
        elif self.frequency == rrule.MONTHLY and self.monthly_interval == 'dayofweek':
            if self.monthly_weekday == 7: # Day
                days = (0, 1, 2, 3, 4, 5, 6)
                params['bysetpos'] = self.monthly_ordinal_week
            elif self.monthly_weekday == 8: # Weekday
                days = (0, 1, 2, 3, 4)
                params['bysetpos'] = self.monthly_ordinal_week
            elif self.monthly_weekday == 9: # Weekend day
                days = (5, 6)
                params['bysetpos'] = self.monthly_ordinal_week
            else:
                days = rrule.weekdays[self.monthly_weekday](self.monthly_ordinal_week)
            params['byweekday'] = days
        elif self.frequency == rrule.YEARLY and self.yearly_interval == 'dayofweek':
            if self.yearly_weekday == 7: # Day
                days = (0, 1, 2, 3, 4, 5, 6)
                params['bysetpos'] = self.yearly_ordinal_week
            elif self.yearly_weekday == 8: # Weekday
                days = (0, 1, 2, 3, 4)
                params['bysetpos'] = self.yearly_ordinal_week
            elif self.yearly_weekday == 9: # Weekend day
                days = (5, 6)
                params['bysetpos'] = self.yearly_ordinal_week
            else:
                days = rrule.weekdays[self.yearly_weekday](self.yearly_ordinal_week)
            params['byweekday'] = days

        # bymonthday
        if self.frequency == rrule.MONTHLY and self.monthly_interval == 'dayofmonth':
            # Make sure to recur when the month has less then the required
            # day. So, when selecting 31/30/29 it will also recur on months
            # with less days: http://labix.org/python-dateutil#line-516
            params['bysetpos'] = 1
            params['bymonthday'] = (self.monthly_interval_day, -1)
        elif self.frequency == rrule.YEARLY and self.yearly_interval == 'dayofmonth':
            params['bymonthday'] = self.yearly_interval_day

        # bymonth
        if self.frequency == rrule.YEARLY:
            if self.yearly_interval == 'dayofmonth':
                params['bymonth'] = [self.yearly_month1]
            elif self.yearly_interval == 'dayofweek':
                params['bymonth'] = [self.yearly_month2]

        # interval
        if self.frequency == rrule.DAILY and self.daily_interval == 'day':
            params['interval'] = self.daily_interval_number
        elif self.frequency == rrule.WEEKLY:
            params['interval'] = self.weekly_interval_number
        elif self.frequency == rrule.MONTHLY:
            if self.monthly_interval == 'dayofmonth':
                params['interval'] = self.monthly_interval_number1
            elif self.monthly_interval == 'dayofweek':
                params['interval'] = self.monthly_interval_number2

        # count
        if self.range_name == 'count' and self.range_count:
            params['count'] = self.range_count

        # until
        if self.range_name == 'until' and self.end_date:
            until = DT2dt(DateTime(self.end_date))
            until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
            params['until'] = until

        return rrule.rrule(self.frequency, **params)
