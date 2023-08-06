from refaction.tests import *

class TestDbController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='db'))
        # Test response...
