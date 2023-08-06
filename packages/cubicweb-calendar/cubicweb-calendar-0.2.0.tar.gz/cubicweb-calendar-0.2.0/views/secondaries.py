from logilab.mtconverter import html_escape

from cubicweb.view import EntityView
from cubicweb.selectors import implements
from cubicweb.web.views import baseviews

# out of context  ####################################################################


class RecurrentDayOutOfContext(baseviews.OutOfContextView):
    __select__ = implements('Recurrentday')

    def cell_call(self, row, col):
        entity = self.entity(row,col)
        self.w(u'<a href="%s">' % html_escape(entity.absolute_url(vid='edition')))
        self.wdata(entity.dc_long_title())
        self.w(u'</a>')

class TimePeriodOutOfContext(baseviews.OutOfContextView):
    __select__ = implements('Timeperiod')

    def cell_call(self, row, col):
        entity = self.entity(row,col)
        self.w(u'<a href="%s">' % html_escape(entity.absolute_url(vid='edition')))
        self.wdata(entity.dc_long_title())
        self.w(u'</a>')


