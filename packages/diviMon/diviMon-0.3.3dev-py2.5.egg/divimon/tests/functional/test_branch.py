from divimon.tests import *

class TestBranchController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='branch'))
        # Test response...
