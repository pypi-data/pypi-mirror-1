from datetime import timedelta, date, datetime

from logilab.mtconverter import html_escape

from cubicweb.schema import display_name
from cubicweb.utils import date_range, last_day, previous_month, next_month
from cubicweb.view import EntityView
from cubicweb.selectors import implements
from cubicweb.web.views.calendar import CalendarItemView, OneMonthCal
from cubicweb.web.views.old_calendar import _CalendarView

from cubes.calendar.entities import BadCalendar


CALENDARS_PAGE = u"""<table class="bigCalendars">
<tr><td class="calendar">%s</td></tr>
</table>
"""

WORKING_DAYS = ('working')
NON_WORKING_DAYS = ('non_working', 'conges_journee', 'maladie_journee',
                    'conges_mpaternite', 'greve_journee')

WORKING_AM_DAYS = ('working_am','maladie_apresmidi', 'conges_apresmidi',
                   'greve_apresmidi')
WORKING_PM_DAYS = ('working_pm','conges_matin', 'maladie_matin',
                   'greve_matin')

AM_TYPES = ('working_am','conges_matin', 'maladie_matin')
PM_TYPES = ('working_pm','maladie_apresmidi' ,'conges_apresmidi')

WORKING_HALF_DAYS = list(WORKING_AM_DAYS) + list(WORKING_PM_DAYS)


class ActivityMonthCalendarView(_CalendarView):
    """this viewca renders a 3x1 calendars' table"""
    id = 'calendaronemonth'
    title = _('calendar (one month)')

    def nav_header(self, curdate):
        self.req.add_js('cubicweb.ajax.js')
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = self.req.url_quote(self.rset.printable_rql())
        prevlink = self.req.build_ajax_replace_url('onemonthcal', rql, 'calendaronemonth',
                                                   year=prevdate.year,
                                                   month=prevdate.month)
        nextlink = self.req.build_ajax_replace_url('onemonthcal', rql, 'calendaronemonth',
                                                   year=nextdate.year,
                                                   month=nextdate.month)
        self.w(u"""<table class="calendarPageHeader">
<tr><td class="prev"><a href="%s">&lt;&lt;</a></td>
<td class="next"><a href="%s">&gt;&gt;</a></td></tr>
</table>""" % (html_escape(prevlink), html_escape(nextlink)))


    def call(self, year=None, month=None):
        _today = date.today()
        year = int(self.req.form.get('year', _today.year))
        month = int(self.req.form.get('month', _today.month))
        center_date = date(year, month, 1)
        begin, end = self.get_date_range(day=center_date, shift=0)
        schedule = self._mk_schedule(begin, end)
        calendars = self.build_calendars(schedule, begin, end)
        self.w(u'<div id="onemonthcal">')
        self.nav_header(center_date)
        self.w(CALENDARS_PAGE % tuple(calendars))
        self.w(u'</div>')


def get_date_range_from_req(req, year=None, month=None):
    """return (firstday, lastday)"""
    year = year or req.form.get('year')
    month = month or req.form.get('month')
    if year and month:
        year = int(year)
        month = int(month)
        firstday = date(year, month, 1)
    else:
        _today = datetime.today()
        firstday = date(_today.year, _today.month, 1)
    return firstday, last_day(firstday)

class EuserMonitorCalendar(EntityView):
    id = 'user_activity_calendar'
    __select__ = implements('CWUser',)

    def cell_call(self, row, col, year=None, month=None, calid=None):
        self.req.add_js('cubicweb.ajax.js')
        self.req.add_css('cubes.calendar.css')
        user = self.entity(row, col)
        calid = calid or 'tid%s' % user.eid
        firstday, lastday = get_date_range_from_req(self.req, year, month)

        # make calendar
        caption = '%s %s' % (self.req._(firstday.strftime('%B').lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(firstday, user, calid)
        prevlink = '<a href="%s">&lt;&lt;</a>' % html_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % html_escape(nexturl)

        # build cells
        try:
            celldatas = self._build_activities(user, firstday, lastday)
        except BadCalendar, exc: # in case of missing week day information
            self.w(u'<div class="error">%s</div>' % exc)
            return
        # build table/header
        self.w(u'<table id="%s" class="activitiesCal">'
               u'<tr><th class="prev">%s</th>'
               u'<th class="calTitle" colspan="5"><span>%s</span></th>'
               u'<th class="next">%s</th></tr>'
               u'<tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr>'
               % (calid, prevlink, caption, nextlink))
        start = firstday - timedelta(firstday.weekday())
        stop = lastday + timedelta(6 - lastday.weekday())
        for curdate in date_range(start, stop):
            if curdate == start or curdate.weekday() == 0: # sunday
                self.w(u'<tr>')
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w(u'</tr>')
        self.w(u'</table>')

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w(u'<td class="outofrange"></td>')
        else:
            cssclasses, total_duration, url, workcases = celldatas[curdate]
            total = total_duration
            if workcases:
                total = u"%s (%s)" % (total, workcases)
            cellcontent = u'<a title="total %s" href="%s">%s</a>' % (
                total, url, curdate.day)
            self.w(u'<td class="%s">%s</td>' % (u' '.join(cssclasses),  cellcontent))

    def _prevnext_links(self, curdate, user, calid):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = 'Any X WHERE X eid %s' % user.eid
        prevlink = self.req.build_ajax_replace_url(calid, rql, 'user_activity_calendar',
                                                   replacemode='swap',
                                                   month=prevdate.month, year=prevdate.year)
        nextlink = self.req.build_ajax_replace_url(calid, rql, 'user_activity_calendar',
                                                   replacemode='swap',
                                                   month=nextdate.month, year=nextdate.year)
        return prevlink, nextlink

    def _build_activities(self, user, firstday, lastday):
        # figure out which days of month are working days
        resource = user.default_resource
        if resource:
            day_types = dict((date, (dtype, state)) for date, dtype, state in
                             user.reverse_euser[0].get_day_types(firstday, lastday))
        else:
            day_types = {}
        working_dtype = {}
        for eid, state in set(day_types.values()):
            working_dtype[eid] = self.req.eid_rset(eid).get_entity(0, 0)

        # get activities
        activities = {}
        workcases = {}
        pending_activities = set()
        rql = ("Any DI,DU,S,WR WHERE A is Activity, "
               "  A in_state ST, ST name S, "
               "  A diem <= %(l)s, A diem >= %(f)s, "
               "  A diem DI, A duration DU, "
               "  A done_by R, R euser U, U eid %(u)s, "
               "  A done_for WO, W split_into WO, W title WR")
        rset = self.req.execute(rql, {'u': user.eid, 'l': lastday, 'f': firstday})
        for diem, duration, state, workcase in rset:
            activities.setdefault(diem, 0)
            workcases.setdefault(diem, [])
            activities[diem] += float(duration)
            workcases[diem].append(workcase)
            if state == 'pending':
                pending_activities.add(diem)

        # build result
        celldatas = {}
        _today = date.today()
        for date_ in date_range(firstday, lastday):
            cssclass = []
            total_duration = activities.get(date_, 0.)
            dtype, state = day_types.get(date_, (None, None))
            if state == 'pending':
                cssclass.append(u'daytype_pending')
            if dtype and working_dtype[dtype].work_during:
                if date_ <= _today:
                    dtype_title = working_dtype[dtype].title
                    if ((total_duration != 1. and  dtype_title in WORKING_DAYS) or
                        (total_duration != 0.5 and dtype_title in WORKING_HALF_DAYS)):
                        cssclass.append(u'problem')
                    else:
                        if date_ in pending_activities:
                            cssclass.append(u'pending')
                        else:
                            cssclass.append(u'completed')
                    if dtype_title in WORKING_DAYS:
                        total_duration = u'%s / 1.0' % total_duration
                    elif dtype_title in WORKING_HALF_DAYS:
                        total_duration = u'%s / 0.5' % total_duration
                else:
                    if total_duration:
                        cssclass.append(u'problem')
            else:
                if state != 'pending':
                    cssclass.append(u'closed')
                if total_duration:
                    cssclass.append(u'problem')
            a_rql = ("Any A WHERE A is Activity, A diem = '%(d)s', "
                     "A done_by R, R euser U, U eid %(u)s"
                     % {'u': user.eid, 'd': date_.strftime('%Y-%m-%d')})
            url = html_escape(self.build_url(rql=a_rql, vid='activities-submit',
                                             year=date_.year, month=date_.month, day=date_.day))
            workcases_str = ','.join(workcases.get(date_, ''))
            celldatas[date_] = (cssclass, total_duration, url, workcases_str)
        if _today in celldatas:
            # celldatas maps days to tuples (cssclass, duration, url, descr)
            celldatas[_today][0].append(u'today')
        return celldatas


class EuserCalendar(EntityView):
    __select__ = implements('Calendar',)
    id = 'user_calendar'

    def cell_call(self, row, col):
        self.req.add_css('cubes.calendar.css')
        entity = self.entity(row, col)
        _today = datetime.today()
        year = int(self.req.form.get('year', _today.year))
        month = int(self.req.form.get('month', _today.month))
        firstday, lastday = get_date_range_from_req(self.req, year, month)
        # make calendar
        caption = '%s %s' % (self.req._(firstday.strftime('%B').lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(entity,firstday)
        prevlink = '<a href="%s">&lt;&lt;</a>' % html_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % html_escape(nexturl)
        self.w(u'<table id="ctid%s" class="userCal">'
               u'<tr><th class="prev">%s</th>'
               u'<th class="calTitle" colspan="6"><span>%s</span></th>'
               u'<th class="next">%s</th></tr>'
               u'<tr><th>&nbsp;</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr>'
               % (entity.eid, prevlink, caption, nextlink))
        start = firstday - timedelta(firstday.weekday())
        stop = lastday + timedelta(6 - lastday.weekday())
        celldatas = self._build_celldata(entity, firstday, lastday)
        # build cells
        for curdate in date_range(start, stop):
            if curdate == start or curdate.weekday() == 0: # sunday
                self.w(u'<tr>')
                self.w(u'<td class="week">%s<br/> %d</td>' % (self.req._('week'), curdate.isocalendar()[1]))
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w(u'</tr>')
        self.w(u'</table>')

    def _prevnext_links(self, entity, curdate):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = 'Any X WHERE X eid %s' % entity.eid
        prevlink = self.req.build_ajax_replace_url('ctid%s' % entity.eid, rql,
                                                   'user_calendar', replacemode='swap',
                                                   month=prevdate.month, year=prevdate.year)
        nextlink = self.req.build_ajax_replace_url('ctid%s' % entity.eid, rql, 'user_calendar',
                                                   replacemode='swap',
                                                   month=nextdate.month, year=nextdate.year)
        return prevlink, nextlink

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w(u'<td class="outofrange"></td>')
        else:
            cssclasses, total_duration, url, workcases = celldatas[curdate]
            stickers = u' '.join(cssclasses)
            pending = self.req._('pending')

            klasses=[]
            am_stickers=[]
            pm_stickers=[]
            for cssclass in cssclasses:
                klass = cssclass.split(':')[0]
                pending_suffix = cssclass.endswith(':pending') and '_pending' or ''
                if curdate == datetime.today():
                    klasses.append(u'today')
                if klass in NON_WORKING_DAYS:
                    klasses.append(u'non_working'+pending_suffix)
                    am_stickers.append(self.req._(klass))
                    pm_stickers.append(self.req._(klass))
                elif klass in WORKING_PM_DAYS:
                    klasses.append(u'working_pm'+pending_suffix)
                    if klass in AM_TYPES:
                        am_stickers.append(self.req._(klass))
                        pm_stickers.append(self.req._('working'))
                    else:
                        am_stickers.append(self.req._('non_working'))
                        pm_stickers.append(self.req._(klass))
                elif klass in WORKING_AM_DAYS:
                    klasses.append(u'working_am'+pending_suffix)
                    if klass in AM_TYPES:
                        am_stickers.append(self.req._(klass))
                        pm_stickers.append(self.req._('non_working'))
                    else:
                        am_stickers.append(self.req._('working'))
                        pm_stickers.append(self.req._(klass))
                elif klass in WORKING_DAYS:
                    klasses.append(u'working'+pending_suffix)
                    am_stickers.append(self.req._(klass))
                    pm_stickers.append(self.req._(klass))
                else:
                    self.error('Unknown daytype class %s', klass)
            am_cell ='<tr><td class="am"><div class="mday">am</div><div class="stickers">%s</div></td></tr>\n' % (' '.join(am_stickers))
            pm_cell ='<tr><td class="pm"><div class="mday">pm</div><div class="stickers">%s</div></td></tr>\n' % (' '.join(pm_stickers))
            cell_url = u'<a title="total %s" href="%s">%s</a>' % (total_duration, url, curdate.day)
            # FIXME cell_url
            cellcontent = u'<table class="caldata">'
            cellcontent +='<tr><td class="caldate">%s</td></tr>%s %s</table>' % (cell_url,  am_cell, pm_cell)
            self.w(u'<td class="%s" title="%s">%s</td>' %(' '.join(klasses), html_escape(stickers),  cellcontent))

    def _build_celldata(self, entity, firstday, lastday):
        celldatas = {}
        for date, dtype, state in entity.get_days_type(firstday, lastday):
            cssclass = []
            if dtype is None:
                cssclass.append(u'unknown')
            else:
                dtype = self.req.eid_rset(dtype).get_entity(0, 0)
                if state == 'pending':
                    cssclass.append('%s:%s' % (dtype.title,state))
                else:
                    cssclass.append(dtype.title)
            celldatas[date] = (cssclass, 0, '', '')
        return celldatas

class TimeperiodCalendarItemView(EntityView):
    id = 'calendaritem'
    __select__ = implements('Timeperiod',)
    def cell_call(self, row, col):
        entity = self.complete_entity(row, col)
        day_types = u' '.join(self.req._(dt.title) for dt in entity.day_type)
        calendar = entity.from_calendar
        self.w(html_escape(u'%s : %s (%s)' % (calendar.title, day_types, self.req._(entity.state))))
