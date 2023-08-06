from smsshell.tests import *

class TestFilterController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='filter'))
        # Test response...
