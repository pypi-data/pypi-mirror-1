from cubicweb.selectors import implements
from cubicweb.web.facet import RelationFacet

class TimeperiodCalendarFacet(RelationFacet):
    id = 'timeperiod-calendar-facet'
    __select__ = RelationFacet.__select__ & implements('Timeperiod',)
    rtype = 'periods'
    target_attr = 'title'
