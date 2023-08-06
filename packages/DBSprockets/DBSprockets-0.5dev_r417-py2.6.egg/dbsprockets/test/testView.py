from dbsprockets.view import View
from tw.api import Widget
from dbsprockets.viewconfig import ViewConfig
from dbsprockets.metadata import Metadata
from dbsprockets.iprovider import IProvider

class testView:
    def setup(self):
        provider = IProvider()
#        metadata = Metadata(provider)
        view_config = ViewConfig(provider, '')

        self.view = View(Widget(), view_config)

    def test_create(self):
        pass

    def testDisplay(self):
        s = self.view.widget(value={})
        assert s == None, s