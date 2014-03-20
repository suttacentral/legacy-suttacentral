import unittest
import sc

from sc import I18N
from sc.exceptions import NoSuchLanguageError, NoSuchTranslationError

class Nameable:
    """ Used for test_find_name """
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

class I18NTest(unittest.TestCase):
    def test_read_data(self):
        i18n = I18N.I18N()
        i18n.file_name = 'test_I18N.csv'
        i18n.read_data()

        # Here is a translation that exists.
        self.assertEqual(i18n.get_translation('en', 'key1'), 'en1')

        # This one doesn't exist
        with self.assertRaises(NoSuchTranslationError):
            self.assertEqual(i18n.get_translation('en', 'key666'), '')

        # This language doesn't exist
        with self.assertRaises(NoSuchLanguageError):
            self.assertEqual(i18n.get_translation('en666', 'key666'), '')
    
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

        with self.assertRaises(NoSuchTranslationError):
            _ = i18n.get_translation('en', '00')

        with self.assertRaises(NoSuchLanguageError):
            _ = i18n.get_translation('00', '00')
        
    def test_language_exists(self):
        i18n = I18N.I18N()
        self.assertFalse(i18n.language_exists('en'))
        i18n.add_language('en')
        self.assertTrue(i18n.language_exists('en'))

    def test_find_name(self):
        translatable = Nameable('uid111', 'Translatable')
        not_translatable = Nameable('uid222', 'Not Translatable')

        i18n = I18N.I18N()
        i18n.add_language('en')
        i18n.add_translation('en', 'uid111', 'Has been translated')

        # uid111 has a translation
        translation = i18n.find_name('en', translatable)
        self.assertEqual(translation, 'Has been translated')
        
        # uid222 does not, so instead we get the untranslated name.
        original_name = i18n.find_name('en', not_translatable)
        self.assertEqual(original_name, 'Not Translatable')

    @unittest.skip('\nNot sure how to test this independently.')  
    def test_get_language(self):
        i18n = I18N.I18N()
