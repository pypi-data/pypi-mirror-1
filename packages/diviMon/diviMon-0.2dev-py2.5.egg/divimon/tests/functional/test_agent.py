from divimon.tests import *

class TestAgentController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='agent'))
        # Test response...
