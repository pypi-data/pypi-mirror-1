from subicpos.tests import *

class TestClassificationController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='classification'))
        # Test response...
