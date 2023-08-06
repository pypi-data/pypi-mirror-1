from salvationfocus.tests import *

class TestGetprebelieverController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='getprebeliever'))
        # Test response...
