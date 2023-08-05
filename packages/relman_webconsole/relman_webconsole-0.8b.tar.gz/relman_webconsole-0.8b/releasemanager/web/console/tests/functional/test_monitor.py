from releasemanager.web.console.tests import *

class TestMonitorController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='monitor'))
        # Test response...