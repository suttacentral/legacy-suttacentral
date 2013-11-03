from selenium.common.exceptions import NoSuchElementException
from environment import SCTestCase

class UrlTestCase(SCTestCase):

    def test_division_without_subdivisions_view(self):
        self.goto('/dn')
        self.assertIn('Dīgha Nikāya', self.table_heading_text())

    def test_division_with_subdivisions_headings_view(self):
        self.goto('/kn')
        self.assertIn('Khuddaka Nikāya', self.table_heading_text())

    def test_division_with_subdivisions_full_view(self):
        self.goto('/kn/full')
        self.assertIn('Khuddaka Nikāya', self.table_heading_text())

    def test_sutta_pali_page(self):
        self.goto('/dn1/pi')
        self.assertIn('Brahmajālasutta', self.article_header_text())

    def test_translation_page(self):
        self.goto('/dn1/en')
        self.assertIn('Net of Views', self.article_header_text())

    def test_bug_34_regression(self):
        self.goto('/it')
        self.assertIn('Itivuttaka', self.table_heading_text())
        self.goto('/sa')
        self.assertIn('Saṃyuktāgama', self.table_heading_text())
        self.goto('/sa/full')
        self.assertIn('Saṃyuktāgama', self.table_heading_text())

    def test_bug_35_regression(self):
        self.goto('/up1.021/en')
        self.assertIn('Upāyikā 1.021', self.article_header_text())
        self.goto('/up2.071/en')
        self.assertIn('Upāyikā 2.071', self.article_header_text())

    def test_bug_42_regression(self):
        self.goto('/dq')
        self.assertTableHasRows()
        self.goto('/up')
        self.assertTableHasRows()
        self.goto('/avs')
        self.assertTableHasRows()
        self.goto('/divy')
        self.assertTableHasRows()
        self.goto('/lal')
        self.assertTableHasRows()
        self.goto('/mvu')
        self.assertTableHasRows()
        self.goto('/sbv')
        self.assertTableHasRows()

    def table_heading_text(self):
        return self.css('caption').text

    def article_header_text(self):
        return self.css('article h1').text

    def assertTableHasRows(self, n=1):
        self.css('table tr:nth-child({})'.format(n+1))
