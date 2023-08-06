import unittest 
import localdatetime
from DateTime import DateTime

class BaseTestCase(unittest.TestCase):
    def get_datetime_tuple(self, dt):
        return [int(p) for p in dt.parts()[:6]]
        
    def test_getFormattedDate(self):
        # test some dates from different locales
        dt = self.get_datetime_tuple(DateTime('2005-02-01 19:13'))
        
        fd = localdatetime.getFormattedDate(None, dt, size="short", locale="nl")
        self.assertEquals(u'1-2-05 19:13', fd)

        fd = localdatetime.getFormattedDate(None, dt, size="medium", locale="nl")
        self.assertEquals(u'1-feb-2005 19:13:00', fd)

        fd = localdatetime.getFormattedDate(None, dt, size="long", locale="nl")
        self.assertEquals(u'1 februari 2005 19:13:00 +000', fd)

        fd = localdatetime.getFormattedDate(None, dt, size="full", locale="nl")
        self.assertEquals(u'dinsdag 1 februari 2005 19:13:00 uur +000', fd)

        fd = localdatetime.getFormattedDate(None, dt, size="short", locale="en")
        self.assertEquals(u'2/1/05 7:13 PM', fd)

        fd = localdatetime.getFormattedDate(None, dt, size="short", locale="en-za")
        self.assertEquals(u'2005/02/01 7:13 PM', fd)

    def test_getMonthNames(self):
        # test the month names of certain locales
        months = localdatetime.getMonthNames(None, 'nl')
        self.assertEquals([u'januari', u'februari', u'maart', u'april', 
                    u'mei', u'juni', u'juli', u'augustus', u'september', 
                    u'oktober', u'november', u'december'], months)

        monthabbrs = localdatetime.getMonthAbbreviations(None, 'nl')
        self.assertEquals([u'jan', u'feb', u'mrt', u'apr', u'mei', u'jun', 
                    u'jul', u'aug', u'sep', u'okt', u'nov', u'dec'],
                    monthabbrs)

def test_suite():
    suite = unittest.TestSuite()
    for testcase in (BaseTestCase,):
        suite.addTest(unittest.makeSuite(testcase))
    return suite

if __name__ == '__main__':
    unittest.main()
