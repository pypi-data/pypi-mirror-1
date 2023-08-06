from frla.tests import *

class TestBilgikisiController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='bilgikisi'))
        # Test response...
