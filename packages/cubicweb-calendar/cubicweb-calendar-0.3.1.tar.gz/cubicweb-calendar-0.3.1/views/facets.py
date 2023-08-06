from cubicweb.selectors import implements
from cubicweb.web.facet import RelationFacet

class TimeperiodCalendarFacet(RelationFacet):
    __regid__ = 'timeperiod-calendar-facet'
    __select__ = RelationFacet.__select__ & implements('Timeperiod',)
    rtype = 'periods'
    target_attr = 'title'
