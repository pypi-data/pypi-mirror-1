from ispmanccp.tests import *

class TestLockedController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='locked'))
        # Test response...