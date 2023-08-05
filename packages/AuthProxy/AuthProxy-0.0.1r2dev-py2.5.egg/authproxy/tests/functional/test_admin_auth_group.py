from authproxy.tests import *

class TestAuthGroupController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='admin/auth_group'))
        # Test response...
