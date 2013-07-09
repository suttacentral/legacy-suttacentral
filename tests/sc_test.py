from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(realpath(__file__))), 'python'))

import config, os, time, unittest
from urllib.parse import urljoin
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

class ScTest(unittest.TestCase):

    # Pass any unknown method to browser
    def __getattr__(self, name):
        return getattr(self.browser, name)

    def setUp(self):
        global base_url, browser
        self.base_url = base_url
        self.browser = browser

    def goto(self, path):
        self.get(urljoin(self.base_url, path))

    def css(self, selector):
        return self.browser.find_element_by_css_selector(selector)

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
        self.assertEqual('en | en | en | fr | de | vn',
                          self.css('.origin td:last-child').text)

if __name__ == '__main__':
    try:
        local_url = 'http://%s:%d/' % (config['global']['server.socket_host'],
                                       config['global']['server.socket_port'])
        base_url = os.getenv('URL', local_url)
        browser = webdriver.Firefox()
        unittest.main()
    finally:
        browser.close()
