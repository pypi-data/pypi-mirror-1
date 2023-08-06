from salvationfocus.tests import *

class TestBelieverController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='believer'))
        # Test response...
