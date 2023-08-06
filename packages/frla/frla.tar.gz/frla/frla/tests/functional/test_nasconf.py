from frla.tests import *

class TestNasconfController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='nasconf'))
        # Test response...
