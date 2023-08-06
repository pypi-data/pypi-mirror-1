from subicpos.tests import *

class TestTransactionController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='transaction'))
        # Test response...
