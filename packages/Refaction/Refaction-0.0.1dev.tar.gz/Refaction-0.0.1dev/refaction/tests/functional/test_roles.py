from refaction.tests import *

class TestRolesController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='roles'))
        # Test response...
