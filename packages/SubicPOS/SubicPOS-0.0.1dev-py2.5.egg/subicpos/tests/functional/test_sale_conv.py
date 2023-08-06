from subicpos.tests import *

class TestSaleConvController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='sale_conv'))
        # Test response...
