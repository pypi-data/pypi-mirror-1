from restin.tests import *

class TestApplicationsController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='App'))
        # Test response...
