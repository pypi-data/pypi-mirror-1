from authproxy.tests import *

class TestAuthRoleController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='admin/auth_role'))
        # Test response...
