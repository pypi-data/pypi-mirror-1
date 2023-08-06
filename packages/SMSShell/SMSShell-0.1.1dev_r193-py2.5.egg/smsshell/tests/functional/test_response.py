from smsshell.tests import *

class TestResponseController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='response'))
        # Test response...
