from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(realpath(__file__))), 'python'))

import atexit, os, time, unittest
from urllib.parse import urljoin
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import config

base_url = None
browser = None

class SCTestCase(unittest.TestCase):

    # Pass any unknown method to browser
    def __getattr__(self, name):
        return getattr(self.browser, name)

    @property
    def base_url(self):
        global base_url
        if not base_url:
            local_url = 'http://%s:%d/' % (config['global']['server.socket_host'],
                                           config['global']['server.socket_port'])
            base_url = os.getenv('URL', local_url)
        return base_url

    @property
    def browser(self):
        global browser
        if not browser:
            browser = webdriver.Firefox()
            atexit.register(browser.close)
        return browser

    def goto(self, path):
        self.get(urljoin(self.base_url, path))

    def css(self, selector):
        try:
            return self.browser.find_element_by_css_selector(selector)
        except NameError:
            # This is a bug in selenium. It raises a NameError with
            # global name 'basestring' is not defined.
            # See https://code.google.com/p/selenium/issues/detail?id=5701
            raise NoSuchElementException(
                'Could not find by css selector {}'.format(selector))
