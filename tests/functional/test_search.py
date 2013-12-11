from ..helper import SCTestCase, Keys

class SearchTestCase(SCTestCase):

    def test_bug_65_regression(self):
        self.goto('/')
        assert 'body' == self.active_element.tag_name

    def test_tab_focuses_search_input(self):
        self.goto('/')
        self.active_element.send_keys(Keys.TAB)
        assert 'input' == self.active_element.tag_name
        parent_element = self.active_element.find_element_by_xpath('..')
        assert 'page-header-search' == parent_element.get_attribute('id')
