"""template-specific forms/views/actions/components"""
from cubicweb.web import uicfg

_afs = uicfg.autoform_section
_afs.tag_object_of(('*', 'periods', 'Timeperiod'), 'main', 'attributes')
_afs.tag_object_of(('*', 'periods', 'Timeperiod'), 'muledit', 'attributes')

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Calendar', 'weekdays', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'days', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'periods', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'day_types', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'inherits', '*'), 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
for rtype in ('days', 'weekdays', 'periods', 'day_types', 'inherits'):
    _abaa.tag_subject_of(('Calendar', rtype, '*'), True)
_abaa.tag_subject_of(('Daytype', 'work_during', '*'), True)
_abaa.tag_object_of(('Calendar', 'inherits', '*'), True)
_abaa.tag_object_of(('*', 'for_calendar', 'Calendar'), True)
_abaa.tag_object_of(('*', 'for_period', 'Timeperiod'), True)

