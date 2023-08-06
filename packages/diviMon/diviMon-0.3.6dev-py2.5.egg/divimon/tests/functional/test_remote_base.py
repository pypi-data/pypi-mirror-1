from divimon.tests import *

class TestBaseController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='remote/base'))
        # Test response...
