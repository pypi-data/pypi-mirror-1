from smsshell.tests import *

class TestSentController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='sent'))
        # Test response...
