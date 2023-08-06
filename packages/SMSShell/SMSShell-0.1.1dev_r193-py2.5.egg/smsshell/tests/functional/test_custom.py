from smsshell.tests import *

class TestCustomController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='custom'))
        # Test response...
