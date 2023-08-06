from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Calendar', 'Calendaruser', 'Daytype',
                    'Timespan', 'Timeperiod',
                    'WeekDay', 'Recurrentday',
                    'CWUser'))

    def list_startup_views(self):
        return ()

if __name__ == '__main__':
    unittest_main()
