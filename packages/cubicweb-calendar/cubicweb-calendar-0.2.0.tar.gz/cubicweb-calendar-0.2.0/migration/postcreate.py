# postcreate script. You could setup a workflow here for example

## TIMESPANS
morning = rql('INSERT Timespan TS: TS start "08:00:00", TS stop "12:00:00"').rows[0][0]
afternoon = rql('INSERT Timespan TS: TS start "13:00:00", TS stop "17:00:00"').rows[0][0]

## DAY TYPES
# register day types to i18n catalog
_('working'), _('non_working'), _('working_am'), _('working_pm')
# insertion of Daytype entities
dtype_working = rql('INSERT Daytype DT: DT title "working", DT work_during TM, DT work_during TA '
                    'WHERE TM eid %(tm)s, TA eid %(ta)s',
                    {'tm' : morning, 'ta' : afternoon}).rows[0][0]
dtype_nonworking = rql('INSERT Daytype DT: DT title "non_working"').rows[0][0]
dtype_working_am = rql('INSERT Daytype DT: DT title "working_am", '
                       'DT work_during TA WHERE TA eid %(ta)s',
                       {'ta' : morning}).rows[0][0]
dtype_working_pm = rql('INSERT Daytype DT: DT title "working_pm", '
                       'DT work_during TP WHERE TP eid %(tp)s',
                       {'tp' : afternoon}).rows[0][0]

## WEEK DAYS
for day in (u'monday', u'tuesday', u'wednesday', u'thursday', u'friday'):
    rql('INSERT WeekDay WD: WD day_of_week %(day)s, WD day_type DT '
        'WHERE DT eid %(dt)s',
        {'day' : day, 'dt' : dtype_working})

for day in (u'saturday', u'sunday'):
    rql('INSERT WeekDay WD: WD day_of_week %(day)s, WD day_type DT '
        'WHERE DT eid %(dt)s',
        {'day': day, 'dt' : dtype_nonworking})

## DEFAULT CALENDAR
defaultcal = rql('INSERT Calendar C: C title "Calendrier Francais"').rows[0][0]

rql('SET C weekdays WD WHERE WD is WeekDay, C eid %(cal)s', {'cal' : defaultcal})
rql('SET C day_types DT WHERE DT is Daytype, C eid %(cal)s', {'cal' : defaultcal})

# Timeperiod workflow
wf = add_workflow('time-period workflow', 'Timeperiod')
tp_pending = wf.add_state(_('pending'), initial=True)
tp_validated  = wf.add_state(_('validated'))
wf.add_transition(_('validate'), tp_pending, tp_validated, ('managers',))

