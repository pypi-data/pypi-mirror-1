from dbsprockets.viewfactory import ViewFactory
from dbsprockets.viewconfig import ViewConfig
from dbsprockets.metadata import Metadata, NotFoundError
from dbsprockets.iprovider import IProvider

class DummyMetadata(Metadata):
    def _do_keys(self):
        return []


class DummyViewConfig(ViewConfig):
    metadata_type = DummyMetadata

class testViewFactory:
    def setup(self):
        provider = IProvider()
        self.view_factory = ViewFactory()
        self.view_config = DummyViewConfig(provider, 'test_table')

    def test_createObj(self):
        pass

    def test_create(self):
        view  = self.view_factory.create(self.view_config)
