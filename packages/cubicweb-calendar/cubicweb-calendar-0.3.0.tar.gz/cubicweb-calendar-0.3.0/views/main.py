from datetime import timedelta, date, datetime

from logilab.mtconverter import xml_escape
from logilab.common.date import date_range, last_day, previous_month, next_month

from cubicweb.schema import display_name
from cubicweb.view import EntityView
from cubicweb.selectors import implements
from cubicweb.web.views.calendar import CalendarItemView, OneMonthCal
from cubicweb.web.views.old_calendar import _CalendarView


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


class ActivityMonthCalendarView(_CalendarView):
    """this viewca renders a 3x1 calendars' table"""
    __regid__ = 'calendaronemonth'
    title = _('calendar (one month)')

    def nav_header(self, curdate):
        self._cw.add_js('cubicweb.ajax.js')
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = self._cw.url_quote(self.cw_rset.printable_rql())
        prevlink = self._cw.build_ajax_replace_url('onemonthcal', rql, 'calendaronemonth',
                                                   year=prevdate.year,
                                                   month=prevdate.month)
        nextlink = self._cw.build_ajax_replace_url('onemonthcal', rql, 'calendaronemonth',
                                                   year=nextdate.year,
                                                   month=nextdate.month)
        self.w(u"""<table class="calendarPageHeader">
<tr><td class="prev"><a href="%s">&lt;&lt;</a></td>
<td class="next"><a href="%s">&gt;&gt;</a></td></tr>
</table>""" % (xml_escape(prevlink), xml_escape(nextlink)))


    def call(self, year=None, month=None):
        _today = date.today()
        year = int(self._cw.form.get('year', _today.year))
        month = int(self._cw.form.get('month', _today.month))
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

class EuserCalendar(EntityView):
    __select__ = implements('Calendar',)
    __regid__ = 'user_calendar'

    def cell_call(self, row, col):
        self._cw.add_css('cubes.calendar.css')
        entity = self.cw_rset.get_entity(row, col)
        _today = datetime.today()
        year = int(self._cw.form.get('year', _today.year))
        month = int(self._cw.form.get('month', _today.month))
        firstday, lastday = get_date_range_from_req(self._cw, year, month)
        # make calendar
        caption = '%s %s' % (self._cw._(firstday.strftime('%B').lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(entity,firstday)
        prevlink = '<a href="%s">&lt;&lt;</a>' % xml_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % xml_escape(nexturl)
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
                self.w(u'<td class="week">%s<br/> %d</td>' % (self._cw._('week'), curdate.isocalendar()[1]))
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w(u'</tr>')
        self.w(u'</table>')

    def _prevnext_links(self, entity, curdate):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = 'Any X WHERE X eid %s' % entity.eid
        prevlink = self._cw.build_ajax_replace_url('ctid%s' % entity.eid, rql,
                                                   'user_calendar', replacemode='swap',
                                                   month=prevdate.month, year=prevdate.year)
        nextlink = self._cw.build_ajax_replace_url('ctid%s' % entity.eid, rql, 'user_calendar',
                                                   replacemode='swap',
                                                   month=nextdate.month, year=nextdate.year)
        return prevlink, nextlink

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w(u'<td class="outofrange"></td>')
        else:
            cssclasses, total_duration, url, workcases = celldatas[curdate]
            stickers = u' '.join(cssclasses)
            pending = self._cw._('pending')

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
                    am_stickers.append(self._cw._(klass))
                    pm_stickers.append(self._cw._(klass))
                elif klass in WORKING_PM_DAYS:
                    klasses.append(u'working_pm'+pending_suffix)
                    if klass in AM_TYPES:
                        am_stickers.append(self._cw._(klass))
                        pm_stickers.append(self._cw._('working'))
                    else:
                        am_stickers.append(self._cw._('non_working'))
                        pm_stickers.append(self._cw._(klass))
                elif klass in WORKING_AM_DAYS:
                    klasses.append(u'working_am'+pending_suffix)
                    if klass in AM_TYPES:
                        am_stickers.append(self._cw._(klass))
                        pm_stickers.append(self._cw._('non_working'))
                    else:
                        am_stickers.append(self._cw._('working'))
                        pm_stickers.append(self._cw._(klass))
                elif klass in WORKING_DAYS:
                    klasses.append(u'working'+pending_suffix)
                    am_stickers.append(self._cw._(klass))
                    pm_stickers.append(self._cw._(klass))
                else:
                    self.error('Unknown daytype class %s', klass)
            am_cell ='<tr><td class="am"><div class="mday">am</div><div class="stickers">%s</div></td></tr>\n' % (' '.join(am_stickers))
            pm_cell ='<tr><td class="pm"><div class="mday">pm</div><div class="stickers">%s</div></td></tr>\n' % (' '.join(pm_stickers))
            cell_url = u'<a title="total %s" href="%s">%s</a>' % (total_duration, url, curdate.day)
            # FIXME cell_url
            cellcontent = u'<table class="caldata">'
            cellcontent +='<tr><td class="caldate">%s</td></tr>%s %s</table>' % (cell_url,  am_cell, pm_cell)
            self.w(u'<td class="%s" title="%s">%s</td>' %(' '.join(klasses), xml_escape(stickers),  cellcontent))

    def _build_celldata(self, entity, firstday, lastday):
        celldatas = {}
        for date, dtype, state in entity.get_days_type(firstday, lastday):
            cssclass = []
            if dtype is None:
                cssclass.append(u'unknown')
            else:
                dtype = self._cw.eid_rset(dtype).get_entity(0, 0)
                if state == 'pending':
                    cssclass.append('%s:%s' % (dtype.title,state))
                else:
                    cssclass.append(dtype.title)
            celldatas[date] = (cssclass, 0, '', '')
        return celldatas

class TimeperiodCalendarItemView(EntityView):
    __regid__ = 'calendaritem'
    __select__ = implements('Timeperiod',)
    def cell_call(self, row, col):
        entity = self.complete_entity(row, col)
        day_types = u' '.join(self._cw._(dt.title) for dt in entity.day_type)
        calendar = entity.from_calendar
        self.w(html_escape(u'%s : %s (%s)' % (calendar.title, day_types, self._cw._(entity.state))))
