from nose.tools import eq_
from dbsprockets.widgets.widgets import *
from dbsprockets.test.base import *
from dbsprockets.saprovider import SAProvider

setupDatabase()
provider = SAProvider(metadata)

class TestContainerWidget:
    def setup(self):
        self.widget = ContainerWidget()

    def test_createObj(self):
        pass

    def testDisplay(self):
        s = self.widget.render()
        assert 'class="containerwidget"' in s

class dummy(object):
    pass
class TestFieldViewWidget:
    def setup(self):
        d = dummy
        d.name = 'key'
        self.widget = RecordFieldWidget(identifier=d)

    def test_createObj(self):
        pass

    def testDisplay(self):
        s = self.widget.render({'key':'value'})
        eq_(s, """<tr xmlns="http://www.w3.org/1999/xhtml" class="recordfieldwidget">
    <td>
        <b>key</b>
    </td>
    <td> value
    </td>
</tr>""")

class TestTableViewWidget:
    def setup(self):
        self.widget = TableLabelWidget()

    def test_createObj(self):
        pass

    def testDisplay(self):
        s = self.widget.render()
        assert 'class="tablelabelwidget"' in s

class TestForeignKeySingleSelectField(DBSprocketsTest):
    def setup(self):
        super(TestForeignKeySingleSelectField, self).setup()
        self.widget = ForeignKeySingleSelectField(table_name='tg_user', provider=provider)

    def test_createObj(self):
        pass

    def testDisplay(self):
        s = self.widget.render()
        assert """<select xmlns="http://www.w3.org/1999/xhtml" class="foreignkeysingleselectfield">
        <option value=""" in s, s
