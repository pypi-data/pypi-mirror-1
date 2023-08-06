from darcscgi.tests import *

class TestInformationController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='information', action='index'))
        # Test response...
