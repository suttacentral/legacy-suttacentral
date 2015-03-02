import datetime
import pytz
import unittest

from sc import util

from tests.helper import SCTestCase

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
    
    sortdata1 = ['1x', '1.1x', '1.1.1x', '1.2.1x', '1.2.3x', '1.3x']
    sortdata2 = ['x1', 'x1.1', 'x1.1.1', 'x1.2', 'x1.2.1', 'x1.2.1.1', 'x1.2.2']
    def test_numericsortkey(self):
        # numeric sort only gets one of these cases right.
        data1 = self.sortdata1
        self.assertNotEqual(data1, sorted(data1, key=util.numericsortkey))
        
        data2 = self.sortdata2
        self.assertEqual(data2, sorted(data2, key=util.numericsortkey))
    
    def test_humansortkey(self):
        # human sort gets both correct.
        data1 = self.sortdata1
        self.assertEqual(data1, sorted(data1, key=util.humansortkey))
        
        data2 = self.sortdata2
        self.assertEqual(data2, sorted(data2, key=util.humansortkey))

    def test_recursive_merge(self):
        from copy import deepcopy
        
        a = {1: 2, 2: 4}
        b = {3: 9, 4: 16}

        c = {'z': deepcopy(a)}
        d = {'z': deepcopy(b)}

        util.recursive_merge(a, b)
        self.assertEqual(a, {1: 2, 2:4, 3:9, 4:16})

        util.recursive_merge(c, d)
        self.assertEqual(c, {'z': {1: 2, 2:4, 3:9, 4:16}})

        e = {
            'animals': {
                'pets': {
                    'friendly': ['dogs'],
                    'snobby': ['cats']
                }
            },
            'ready': 0
        }
        
        f = {
            'animals': {
                'pets': {
                    'friendly': ['dogs', 'rats', 'hamsters'],
                    'wet': ['goldfish', 'eels']
                },
                'herbivores': {
                    'plains': ['elephants']
                }
            },
            'ready': True
        }
        util.recursive_merge(e, f)
        self.assertEqual(e, {
            'animals': {
                'pets': {
                    'friendly': ['dogs', 'rats', 'hamsters'],
                    'snobby': ['cats'],
                    'wet': ['goldfish', 'eels']
                },
                'herbivores': {
                    'plains': ['elephants']
                }
            },
            'ready': True
        })
