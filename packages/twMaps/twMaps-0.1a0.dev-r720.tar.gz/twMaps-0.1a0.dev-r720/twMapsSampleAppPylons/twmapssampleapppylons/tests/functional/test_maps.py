from twmapssampleapppylons.tests import *

class TestMapsController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='maps'))
        # Test response...