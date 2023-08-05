from releasemanager.web.console.tests import *

class TestBuildersController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='builders'))
        # Test response...