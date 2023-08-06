from frla.tests import *

class TestDbayarController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='dbayar'))
        # Test response...
