from ispmanccp.tests import *

class TestAccountsController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='accounts'))
        # Test response...
