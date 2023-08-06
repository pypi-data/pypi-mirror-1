from smsshell.tests import *

class TestContactController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='contact'))
        # Test response...
