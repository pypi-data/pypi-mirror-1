from darcscgi.tests import *

class TestTemplateController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='template', action='index'))
        # Test response...
