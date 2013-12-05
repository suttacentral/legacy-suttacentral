import re

from test_env import SCTestCase

class SimpleTestCase(SCTestCase):

    def test_homepage_title(self):
        self.goto('/')
        self.assertIn('Correspondence of early Buddhist discourses', self.title)

    def test_unknown_page(self):
        self.goto('/blargh')
        self.assertPageIs404()

    def test_translation_order(self):
        self.goto('/dn2')
        self.assertEqual('Details for DN 2 Sāmaññaphala',
                          self.css('caption').text)
        self.assertEqual('en | vn | en | en | fr | de',
                          self.css('.origin td:last-child').text)

    def test_scm_footer(self):
        self.goto('/')
        source = self.browser.page_source
        # get the last 5 lines...
        source = '\n'.join(source.split('\n')[-5:])
        self.assertRegex(source, r'Revision: +[0-9a-f]+\n')
        self.assertRegex(source, r'Date: +.+\n')

    DN4_CITATION = re.sub(r'\s{2,}', ' ', """
        Parallels for DN 4 Soṇadaṇḍa (DN i 111): DA 22 (T i 094a18); SHT 1251,
        1352c; SF 42 (HARTMANN, Jens-Uwe 1989. Fragmente aus dem Dīrghāgama der
        Sarvāstivādins. In ENOMOTO Fumio, HARTMANN, Jens-Uwe, and MATSUMURA
        Hisashi (eds), Sanskrit-Texte aus dem buddhistischen Kanon:
        Neuentdeckungen und Neueditionen ( = Sanskrit-Wörterbuch der
        buddhistischen Texte aus den Turfan-Funden, Beiheft 2), Göttingen:
        Vandenhoeck & Ruprecht, 37-67.)
    """.strip())

    def test_parallel_citation(self):
        self.goto('/dn4')
        text_input = self.css('#parallel-citation > input')
        full_citation = text_input.get_attribute('value')
        regex = r'^(.+)\. Retrieved from (.+) on (.+)\.$'
        self.assertRegex(full_citation, regex)
        matches = re.search(regex, full_citation)
        self.assertEqual(self.DN4_CITATION, matches.group(1))
