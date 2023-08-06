from frla.tests import *

class TestTarihController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='tarih'))
        # Test response...
