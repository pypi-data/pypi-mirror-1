from refaction.tests import *

class TestUsersController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='users'))
        # Test response...
