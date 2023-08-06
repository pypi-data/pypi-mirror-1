from darcscgi.tests import *

class TestRepositoriesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='repositories', action='index'))
        # Test response...
