from salvationfocus.tests import *

class TestMainController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='main'))
        # Test response...
