from divimon.tests import *

class TestClientController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='remote/client'))
        # Test response...
