from tw.testutil import WidgetTestCase
from tw.extjs import all

class TestWidget(WidgetTestCase):
    widget = all

    def test_render(self):
        self.assertInOutput('<script')
