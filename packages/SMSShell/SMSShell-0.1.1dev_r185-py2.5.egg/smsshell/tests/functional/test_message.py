from smsshell.tests import *

class TestMessageController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='message'))
        # Test response...
