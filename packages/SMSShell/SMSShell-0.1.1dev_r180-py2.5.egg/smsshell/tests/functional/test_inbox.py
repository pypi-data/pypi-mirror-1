from smsshell.tests import *

class TestInboxController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='inbox'))
        # Test response...
