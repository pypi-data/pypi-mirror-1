from toscawidgets.testutil import WidgetTestCase
from toscawidgets.widgets.rating import *

class TestWidget(WidgetTestCase):
    TestWidget = Rating

    def test_render(self):
        self.assertInOutput('<form')
