from frla.tests import *

class TestTarihbilgisiController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='tarihbilgisi'))
        # Test response...
