from frla.tests import *

class TestAdController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='ad'))
        # Test response...
