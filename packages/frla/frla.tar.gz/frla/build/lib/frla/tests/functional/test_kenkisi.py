from frla.tests import *

class TestKenkisiController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='kenkisi'))
        # Test response...
