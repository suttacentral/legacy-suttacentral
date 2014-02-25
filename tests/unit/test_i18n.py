import unittest
import sc

from sc.I18N import I18N

class I18NTest(unittest.TestCase):
    def test_I18N(self):
        i18n = I18N() #Testing that we can make one of these
        self.assertEqual(i18n.getHello(), 'Hello')
        
