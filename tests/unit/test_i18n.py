import unittest
import sc

from sc import I18N

class I18NTest(unittest.TestCase):
    def test_read_data(self):
        i18n = I18N.I18N()
        i18n.file_name = 'test_I18N.csv'
        i18n.read_data()
    
    def test_add_language(self):
        i18n = I18N.I18N()
        with self.assertRaises(KeyError):
            does_not_exist = i18n.i18n_data['en']
        i18n.add_language('en')
        now_should_exist = i18n.i18n_data['en']
        
