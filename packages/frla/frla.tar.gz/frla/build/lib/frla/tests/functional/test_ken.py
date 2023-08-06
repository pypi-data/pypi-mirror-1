from frla.tests import *

class TestKenController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='ken'))
        # Test response...
