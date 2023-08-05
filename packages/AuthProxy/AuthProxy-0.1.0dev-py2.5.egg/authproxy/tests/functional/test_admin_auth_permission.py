from authproxy.tests import *

class TestAuthPermissionController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='admin/auth_permission'))
        # Test response...
