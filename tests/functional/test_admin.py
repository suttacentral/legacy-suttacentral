from ..helper import SCTestCase

class AdminTestCase(SCTestCase):

    def test_admin_page(self):
        self.goto('/admin')
        self.assertIn('Admin', self.title)
        self.assertIn('Last Updated', self.css('body').text)

    def test_admin_data_notify(self):
        self.goto('/admin/data_notify')
        self.assertIn('Admin', self.title)
        self.assertIn('Last Update Request', self.css('body').text)
