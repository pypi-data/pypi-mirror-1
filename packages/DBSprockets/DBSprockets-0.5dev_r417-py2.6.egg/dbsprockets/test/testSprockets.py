from nose.tools import raises
from tw.api import Widget

from dbsprockets.iprovider import IProvider
from dbsprockets.sprockets import Views, Sessions, Sprocket, Sprockets, SessionConfigError, ViewConfigError
from dbsprockets.view import View
from dbsprockets.sessionconfig import SessionConfig
from dbsprockets.viewconfig import ViewConfig
from dbsprockets.metadata import Metadata

class TestSprockets:
    pass

class TestViews:
    provider = IProvider()
    def setup(self):
        self.views = Views(self.provider, '')

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, provider, controller=''):
        Views(provider, controller)

    def test_create_bad(self):
        provider = IProvider()
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput:
            yield self._create, badInput
        for input in badInput[1:]:
            yield self._create, provider, badInput

    @raises(TypeError)
    def testPutBad(self):
        self.views['lala'] = 'lala'

    def testPut(self):
        view_config = ViewConfig(self.provider,'')
        view = View(Widget, view_config)
        self.views['test'] = view

    @raises(ViewConfigError)
    def testGetBadViewConfigType(self):
        self.views['testBad__table_name']

    def testGet(self):
        view_config = ViewConfig(self.provider,'')
        view = View(Widget, view_config)
        self.views['test'] = view
        assert self.views['test'] == view

    @raises(TypeError)
    def testGetBad(self):
        self.views[1]

class TestSessions:
    provider = IProvider()
    def setup(self):
        self.sessions = Sessions(self.provider)

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1):
        Sessions(arg1)

    def test_create_bad(self):
        badInput = ((), {}, [], 'a', 1, 1.2)
        for input in badInput:
            yield self._create, badInput

    @raises(TypeError)
    def testPutBad(self):
        self.sessions['lala'] = 'lala'

    def testPut(self):
        sessionConfig = SessionConfig('', self.provider)
        self.sessions['test'] = sessionConfig

    def testGet(self):
        sessionConfig = SessionConfig('', self.provider)
        self.sessions['test'] = sessionConfig
        assert self.sessions['test'] is sessionConfig

    @raises(SessionConfigError)
    def testGetBadSessionConfigType(self):
        self.sessions['testBad__table_name']

    @raises(TypeError)
    def testGetBad(self):
        self.sessions[1]

class TestSprocket:
    provider = IProvider()
    sessionConfig = SessionConfig('',provider)
    view_config = ViewConfig(provider, '')
    view = View(Widget, view_config)

    def setup(self):
        self.sprocket = Sprocket(self.view, self.sessionConfig)

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1, arg2=None):
        Sprocket(arg1, arg2)

    def test_create_bad(self):
        badInput = ((), {}, [], 'a', 1, 1.2)
        for input in badInput:
            yield self._create, input

        badInput = ((), {}, [], 'a', 1, 1.2)
        for input in badInput:
            yield self._create, self.view, input

class TestSprockets:
    provider = IProvider()
    def setup(self):
        self.sprockets = Sprockets(self.provider, '')

    def test_create(self):
        pass

    @raises(TypeError)
    def _create(self, arg1, arg2=''):
        Sprockets(arg1, arg2)

    def test_create_bad(self):
        provider = IProvider()
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput:
            yield self._create, badInput
        for input in badInput[1:]:
            yield self._create, provider, badInput

    @raises(TypeError)
    def testPutBad(self):
        self.sprockets['lala'] = 'lala'

    def testPut(self):
        sessionConfig = SessionConfig('', self.provider)
        view_config = ViewConfig(self.provider, '')
        view = View(Widget, view_config)
        sprocket = Sprocket(view, sessionConfig)
        self.sprockets['test'] = sprocket

    def testGet(self):
        sessionConfig = SessionConfig('',self.provider)
        view_config = ViewConfig(self.provider, '')
        view = View(Widget, view_config)
        sprocket = Sprocket(view, sessionConfig)
        self.sprockets['test'] = sprocket
        gotSprocket = self.sprockets['test']
        assert gotSprocket == sprocket

    @raises(TypeError)
    def testGetBad(self):
        self.sprockets[1]