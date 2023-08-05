from authproxy.tests import *

class TestAuthUserController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='admin/auth_user'))
        # Test response...
