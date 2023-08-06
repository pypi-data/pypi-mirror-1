from frla.tests import *

class TestKenbilgisiController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='kenbilgisi'))
        # Test response...
