from smsshell.tests import *

class TestLabelController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='label'))
        # Test response...
