from releasemanager.web.console.tests import *

class TestManagersController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='managers'))
        # Test response...