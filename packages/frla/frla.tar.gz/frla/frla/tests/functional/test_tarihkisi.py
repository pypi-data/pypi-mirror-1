from frla.tests import *

class TestTarihkisiController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='tarihkisi'))
        # Test response...
