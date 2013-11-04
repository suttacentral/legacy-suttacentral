from test_env import SCTestCase

class SimpleTestCase(SCTestCase):

    def test_homepage_title(self):
        self.goto('/')
        self.assertIn('Correspondence of early Buddhist discourses', self.title)

    def test_unknown_page(self):
        self.goto('/blargh')
        self.assertIn('Not Found', self.title)

    def test_translation_order(self):
        self.goto('/dn2')
        self.assertEqual('Details for DN 2 Sāmaññaphala',
                          self.css('caption').text)
        self.assertEqual('en | vn | en | en | fr | de',
                          self.css('.origin td:last-child').text)
