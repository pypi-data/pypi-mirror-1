from divimon.tests import *

class TestSaleController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='sale'))
        # Test response...
