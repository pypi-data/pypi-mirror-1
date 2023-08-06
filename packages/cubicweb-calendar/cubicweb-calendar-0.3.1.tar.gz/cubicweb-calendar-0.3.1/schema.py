# cube's specific schema
from yams.buildobjs import EntityType, SubjectRelation, String, Datetime, Time
from yams.constraints import BoundConstraint, Attribute
from cubicweb.schema import WorkflowableEntityType

_ = unicode

class Calendar(EntityType):
    """see projman"""
    title = String(required=True, unique=True, maxsize=64)
    weekdays = SubjectRelation('WeekDay', cardinality='**')
    days = SubjectRelation('Recurrentday', cardinality='**')
    periods = SubjectRelation('Timeperiod', cardinality = '*1', composite='subject')
    day_types = SubjectRelation('Daytype', cardinality='**')
    inherits = SubjectRelation('Calendar', cardinality='?*')


class Calendaruse(EntityType):
    """see projman"""
    start = Datetime()
    stop = Datetime(constraints=[BoundConstraint('>=', Attribute('start'))])
    use_calendar = SubjectRelation('Calendar', cardinality='1*')


class Daytype(EntityType):
    """see projman"""
    title = String(required=True, maxsize=32, internationalizable=True)
    work_during = SubjectRelation('Timespan', cardinality='**')


class Timespan(EntityType):
    """see projman"""
    start = Time(required=True)
    stop = Time(required=True,
                constraints=[BoundConstraint('>=', Attribute('start'))])


class Timeperiod(WorkflowableEntityType):
    """ """
    start = Datetime(required=True)
    stop = Datetime(required=True,
                    constraints=[BoundConstraint('>=', Attribute('start'))],
                    description=_('last day of the timeperiod'))
    day_type = SubjectRelation('Daytype', cardinality='1*')


class WeekDay(EntityType):
    day_of_week = String(vocabulary=[_('monday'), _('tuesday'), _('wednesday'),
                                     _('thursday'), _('friday'), _('saturday'),
                                     _('sunday')],
                         internationalizable=True)
    day_type = SubjectRelation('Daytype', cardinality='1*')


class Recurrentday(EntityType):
    day_month = String(description='mm-dd', required=True, maxsize=5)
    day_type = SubjectRelation('Daytype', cardinality='1*')
