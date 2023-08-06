from smsshell.tests import *

class TestFolderController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='folder'))
        # Test response...
