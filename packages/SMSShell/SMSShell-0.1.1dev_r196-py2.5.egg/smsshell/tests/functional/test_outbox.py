from smsshell.tests import *

class TestOutboxController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='outbox'))
        # Test response...
