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

    def test_add_translation(self):
        i18n = I18N.I18N()
        i18n.add_language('en')
        
        with self.assertRaises(KeyError):
            does_not_exist = i18n.i18n_data['en']['dn']

        i18n.add_translation('en', 'dn', 'Long Discourses')
        now_should_exist = i18n.i18n_data['en']['dn']

        with self.assertRaises(KeyError):
            does_not_exist = i18n.i18n_data['ab']['dn']
        
    def test_get_translation(self):
        i18n = I18N.I18N()
        i18n.add_language('en')
        i18n.add_translation('en', 'dn', 'Long Discourses')
        self.assertEqual(i18n.get_translation('en', 'dn'), 'Long Discourses')
        # No such key - return empty string
        self.assertEqual(i18n.get_translation('en', '00'), '')
        # No such language - return empty string
        self.assertEqual(i18n.get_translation('00', '00'), '')
        
    def test_language_exists(self):
        i18n = I18N.I18N()
        self.assertFalse(i18n.language_exists('en'))
        i18n.add_language('en')
        self.assertTrue(i18n.language_exists('en'))

    @unittest.skip('\nNot sure how to test this independently.')  
    def test_get_language(self):
        i18n = I18N.I18N()
