import datetime
import pytz
import unittest

import test_env
import util

class UnitsTest(unittest.TestCase):

    test_datetime = datetime.datetime(2011, 4, 19, 4, 32, 4, 0, pytz.UTC)

    def test_format_date_default(self):
        self.assertEquals('19/04/11',
                          util.format_date(self.test_datetime))

    def test_format_datetime_default(self):
        self.assertEquals('19/04/11, 4:32 AM',
                          util.format_datetime(self.test_datetime))

    def test_format_datetime_short(self):
        self.assertEquals('19/04/11, 4:32 AM',
                          util.format_datetime(self.test_datetime, 'short'))

    def test_format_datetime_medium(self):
        self.assertEquals('19/04/2011, 4:32:04 AM',
                          util.format_datetime(self.test_datetime, 'medium'))

    def test_format_datetime_long(self):
        self.assertEquals('19 April 2011 at 4:32:04 AM +0000',
                          util.format_datetime(self.test_datetime, 'long'))

    def test_format_datetime_rfc3339(self):
        self.assertEquals('2011-04-19T04:32:04+00:00',
                          util.format_datetime(self.test_datetime, 'rfc3339'))

    def test_format_time_default(self):
        self.assertEquals('4:32 AM',
                          util.format_time(self.test_datetime))

