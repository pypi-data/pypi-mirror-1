from frla.tests import *

class TestKenyapilandirmaController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='kenyapilandirma'))
        # Test response...
