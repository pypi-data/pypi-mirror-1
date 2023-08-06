from salvationfocus.tests import *

class TestSubmitterController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='submitter'))
        # Test response...
