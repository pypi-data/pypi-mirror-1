from releasemanager.web.console.tests import *

class TestInstallersController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='installers'))
        # Test response...