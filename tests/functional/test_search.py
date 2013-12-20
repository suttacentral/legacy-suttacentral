from selenium.webdriver.common.keys import Keys

from tests.helper import SCTestCase

class SearchTestCase(SCTestCase):

    def test_bug_65_regression(self):
        self.goto('/')
        assert 'body' == self.active_element.tag_name

    def test_bug_69_regression(self):
        self.goto('/search/?query=sutta')
        self.assertIn('You searched: sutta', self.css('body').text)

    def test_tab_focuses_search_input(self):
        self.goto('/')
        self.active_element.send_keys(Keys.TAB)
        assert 'input' == self.active_element.tag_name
        parent_element = self.active_element.find_element_by_xpath('..')
        assert 'page-header-search' == parent_element.get_attribute('id')

    def test_search_dn1(self):
        self.goto('/search?query=dn1')
        query_element = self.css('#main_search_results > div:first-child')
        assert 'You searched: dn1' == query_element.text
        first_row = self.css('#main_search_results table tr:nth-child(3)')
        identifier = first_row.find_element_by_css_selector('td:nth-child(1)')
        title = first_row.find_element_by_css_selector('td:nth-child(2)')
        assert 'DN 1' == identifier.text
        assert 'Brahmajāla' == title.text

    def test_autocomplete(self):
        self.goto('/')
        input_box = self.find_element_by_name('query')
        input_box.click()
        input_box.send_keys('dn2')
        self.implicitly_wait(1)
        first_row = self.css('#page-header-search-results table tr:nth-child(2)')
        identifier = first_row.find_element_by_css_selector('td:nth-child(1)')
        title = first_row.find_element_by_css_selector('td:nth-child(2)')
        assert 'DN 2' == identifier.text
        assert 'Sāmaññaphala' == title.text
