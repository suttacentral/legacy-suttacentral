import datetime
import pytz
import unittest

from ..helper import SCTestCase

import util

class UnitsTest(unittest.TestCase):

    test_datetime = datetime.datetime(2011, 4, 19, 4, 32, 4, 0, pytz.UTC)

    def test_format_date_default(self):
        self.assertEqual('19/04/11',
                         util.format_date(self.test_datetime))

    def test_format_datetime_default(self):
        self.assertEqual('19/04/11, 4:32 AM',
                         util.format_datetime(self.test_datetime))

    def test_format_datetime_short(self):
        self.assertEqual('19/04/11, 4:32 AM',
                         util.format_datetime(self.test_datetime, 'short'))

    def test_format_datetime_medium(self):
        self.assertEqual('19/04/2011, 4:32:04 AM',
                         util.format_datetime(self.test_datetime, 'medium'))

    def test_format_datetime_long(self):
        self.assertEqual('19 April 2011 at 4:32:04 AM +0000',
                         util.format_datetime(self.test_datetime, 'long'))

    def test_format_datetime_rfc3339(self):
        self.assertEqual('2011-04-19T04:32:04+00:00',
                         util.format_datetime(self.test_datetime, 'rfc3339'))

    def test_format_time_default(self):
        self.assertEqual('4:32 AM',
                         util.format_time(self.test_datetime))

    def test_wrap(self):
        input = 'Neither mother, father, nor any other relative can do\n' + \
                'one greater good than one\'s own well-directed mind.'
        output = '   Neither mother, father, nor any other\n' + \
                 '   relative can do\n' + \
                 '   one greater good than one\'s own\n' + \
                 '   well-directed mind.'
        result = util.wrap(input, width=40, indent=3)
        self.assertEqual(output, result)
