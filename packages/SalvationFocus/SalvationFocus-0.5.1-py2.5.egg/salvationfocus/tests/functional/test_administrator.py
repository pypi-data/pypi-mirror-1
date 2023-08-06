from salvationfocus.tests import *

class TestAdministratorController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='administrator'))
        # Test response...
