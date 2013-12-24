import atexit
import os
import sys
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin

from sc import config

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
        """Return a suitable webdriver object.

        See https://selenium.googlecode.com/svn/trunk/docs/api/py/webdriver_remote/selenium.webdriver.remote.webdriver.html
        """
        global browser
        if not browser:
            if os.getenv('PHANTOMJS'):
                browser = webdriver.PhantomJS()
            else:
                browser = webdriver.Firefox()
            atexit.register(browser.close)
        return browser

    @property
    def active_element(self):
        """Return the active DOM element (or body if non selected)."""
        return self.browser.switch_to_active_element()

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

    def assertPageIs404(self):
        self.assertIn('Not Found', self.title)
