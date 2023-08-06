"""template-specific forms/views/actions/components"""
from cubicweb.web import uicfg

uicfg.autoform_section.tag_object_of(('*', 'periods', 'Timeperiod'), 'primary')

uicfg.primaryview_section.tag_subject_of(('Calendar', 'weekdays', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Calendar', 'days', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Calendar', 'periods', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Calendar', 'day_types', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Calendar', 'inherits', '*'), 'hidden')

for rtype in ('days', 'weekdays', 'periods', 'day_types', 'inherits'):
    uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Calendar', rtype, '*'), True)

uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Daytype', 'work_during', '*'), True)

uicfg.actionbox_appearsin_addmenu.tag_object_of(('Calendar', 'inherits', '*'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('*', 'for_calendar', 'Calendar'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('*', 'for_period', 'Timeperiod'), True)

