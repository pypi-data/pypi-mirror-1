from divimon.tests import *

class TestServerController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='remote/server'))
        # Test response...
