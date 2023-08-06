from salvationfocus.tests import *

class TestPrebelieverController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='prebeliever'))
        # Test response...
