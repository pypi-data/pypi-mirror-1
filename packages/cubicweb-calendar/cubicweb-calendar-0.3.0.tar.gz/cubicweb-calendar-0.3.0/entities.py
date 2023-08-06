from logilab.common.date import date_range, todate, todatetime

from cubicweb.interfaces import ICalendarable
from cubicweb.entities import AnyEntity, fetch_config

class BadCalendar(ValueError): pass

def intersect(a,b):
    c = (max(a[0],b[0]), min(a[1], b[1]))
    return c[0] <= c[1]

class Timespan(AnyEntity):
    __regid__ = 'Timespan'
    fetch_attrs, fetch_order = fetch_config(('start', 'stop'))

    def dc_title(self):
        return u'%s - %s' % (self.printable_value('start'),
                             self.printable_value('stop'))

def use_class_cache(cachename, cachepart):
    def cached(func):
        def wrapper(self, *args):
            cache = getattr(self.__class__, cachename).setdefault(cachepart,{})
            cachekey = (self.eid,) + args
            try:
                res = cache[cachekey]
            except KeyError:
                res = func(self, *args)
                cache[cachekey] = res
            return res
        return wrapper
    return cached

class Timeperiod(AnyEntity):
    __regid__ = 'Timeperiod'
    __implements__ = (ICalendarable,)
    fetch_attrs, fetch_order = fetch_config(('start', 'stop'))
    conges_days = [u'conges_journee', u'conges_matin', u'conges_apresmidi']

    def dc_title(self):
        return u'%s-%s' % (self._cw.format_date(self.start),
                           self._cw.format_date(self.stop))

    def dc_long_title(self):
        day_types = u' '.join(self._cw._(dt.title) for dt in self.day_type)
        return u'%s : %s (%s)' % (self.dc_title(), day_types, self._cw._(self.state))

    @property
    def from_calendar(self):
        return self.reverse_periods[0]

class Calendar(AnyEntity):
    __regid__ = 'Calendar'
    rest_attr = 'title'
    fetch_attrs, fetch_order = fetch_config(('title',))
    daytype_cache = {}

    def dc_title(self):
        return self.title

    def parent(self):
        parents = self.inherits
        if parents:
            return parents[0]

    def _fill_cache(self, cache, start, stop):
        # prepare
        periods = self._get_timeperiods()
        rec_days, week_days = self._get_rec_weekdays()
        if self.inherits:
            parent = dict([(item[0], item) for item in self.inherits[0].get_days_type(start, stop)])
        else:
            parent = {}
        # iterate
        for date in date_range(start, stop):
            key = (self.eid, date)
            value = None
            # try period
            for pa, po, ptype, state in periods:
                if pa <= todatetime(date) <= po:
                    value = (self.eid, date, ptype, state)
                    break
            else:
                # try recurrent day
                eid = rec_days.get(date.strftime('%m-%d'))
                if eid is not None:
                    value = (self.eid, date, eid, 'validated')
                else:
                    # try week day
                    eid = week_days.get(date.weekday())
                    if eid is not None:
                        value = (self.eid, date, eid, 'validated')
                    else:
                        if date in parent:
                            value = (self.eid,) + parent[date]
                        else:
                            raise BadCalendar('bad calendar definition, '
                                              'missing week days '
                                              'in root calendar for %s'
                                              % self.eid)
            cache[key] = value

    @use_class_cache('daytype_cache','periods')
    def _get_timeperiods(self):
        rql = ('Any PA,PO,D,SN WHERE C eid %(c)s, C periods P, P day_type D, '
               'P start PA, P stop PO, P in_state S, S name SN')
        rset = self._cw.execute(rql, {'c': self.eid})
        return tuple(rset)

    @use_class_cache('daytype_cache','recweek')
    def _get_rec_weekdays(self):
        # recurrent days
        rql = 'Any D,DM WHERE C eid %(c)s, C days R, R day_month DM, R day_type D'
        rset = self._cw.execute(rql, {'c': self.eid})
        rec_days = dict((row[1], row[0]) for row in rset)
        # week days
        DAYS = [u'monday', u'tuesday', u'wednesday', u'thursday', u'friday', u'saturday', u'sunday']
        rql = 'Any D,W WHERE C eid %(c)s, C weekdays R, R day_of_week W, R day_type D'
        rset = self._cw.execute(rql, {'c': self.eid})
        week_days = dict((DAYS.index(day), eid) for eid, day in rset)
        return rec_days, week_days

    @use_class_cache('daytype_cache','days_type')
    def _get_days_type(self, start, stop):
        """return [(cal_eid, date, day_type_eid, state), ...]
        with state in ('pending', 'validated')
        """
        day_types = []
        cache = self.daytype_cache.setdefault('cal_date', {})
        for date in date_range(start, stop):
            key = (self.eid, todate(date))
            if key not in cache:
                for hole in date_range(date, stop):
                    if (self.eid, hole) in cache:
                        break
                self._fill_cache(cache, date, hole)
            day_types.append(cache[key])
        return day_types

    def _get_daytype_from_titles(self, dtypes):
        """map a set of titles to a set of eids"""
        assert isinstance(dtypes, frozenset), 'dtypes should be a frozenset'
        cache = self.daytype_cache.setdefault('day_title',{})
        if dtypes not in cache:
            types = tuple(dtypes)
            if len(types) == 1:
                rset = self._cw.execute('Any D WHERE D is Daytype, D title %(title)s',
                                        {'title': types[0]})
            else:
                rset = self._cw.execute('Any D WHERE D is Daytype, D title IN %s'
                                        % str(tuple(types)))
            cache[dtypes] = frozenset(row[0] for row in rset)
        return cache[dtypes]

    def get_days_type(self, start, stop, dtypes=None):
        """return [(date, day_type_eid, state), ...] with
        date varying from start to stop"""
        days_type = self._get_days_type(start, stop)
        if dtypes is None:
            return [item[1:] for item in days_type]
        dtype_eids = self._get_daytype_from_titles(frozenset(dtypes))
        return [item[1:] for item in days_type if item[2] in dtype_eids]

class Daytype(AnyEntity):
    __regid__ = 'Daytype'
    fetch_attrs, fetch_order = fetch_config(('title',))

class CalendarUse(AnyEntity):
    __regid__ = 'Calendaruse'
    fetch_attrs, fetch_order = fetch_config(('start', 'stop'))

    @property
    def calendar(self):
        return self.use_calendar[0]

class RecurrentDay(AnyEntity):
    __regid__ = 'Recurrentday'
    fetch_attrs, fetch_order = fetch_config(('day_month', 'day_type'))

    def dc_title(self):
        return self._cw._(self.day_month)

    def dc_long_title(self):
        day_types = u' '.join(dt.title for dt in self.day_type)
        return u'%s : %s' % (self.dc_title(), day_types)

class WeekDay(AnyEntity):
    __regid__ = 'WeekDay'
    fetch_attrs, fetch_order = fetch_config(('day_of_week', 'day_type'))

    def dc_title(self):
        return self._cw._(self.day_of_week)

    def dc_long_title(self):
        day_types = u' '.join(dt.title for dt in self.day_type)
        return u'%s : %s' % (self.dc_title(), day_types)

