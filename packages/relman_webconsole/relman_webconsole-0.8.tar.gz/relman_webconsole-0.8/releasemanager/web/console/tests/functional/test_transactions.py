from releasemanager.web.console.tests import *

class TestTransactionsController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='transactions'))
        # Test response...