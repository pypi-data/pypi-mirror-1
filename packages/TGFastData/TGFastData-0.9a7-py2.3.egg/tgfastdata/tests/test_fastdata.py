
from sqlobject import SQLObject, StringCol, IntCol, connectionForURI

from tgfastdata.datawidgets import FastDataGrid

class FakeUser(SQLObject):
    _connection = connectionForURI("sqlite:///:memory:")

    userId = IntCol()
    name = StringCol()

    def _get_displayName(self):
        return self.name.capitalize()

FakeUser.createTable()

class TestFastDataGrid:
    def setup(self):
        self.grid = FastDataGrid(template = "tgfastdata.templates.datagrid")
    def test_dynamic_fields(self):
        fields = [
                    'userId', 
                    'displayName',
                    ('Name', FakeUser._get_displayName),
                    ('Name', 'displayName'),
                ]
        sr = FakeUser.select()
        d = dict(value=sr, fields=fields)
        self.grid.update_params(d)
        get_field = d['get_field']
        assert ['userId', 'displayName', 'column-2', 'column-3'] == d['collist']
        row = FakeUser(userId=123, name='john')
        assert 123 == get_field(row, 'userId')
        assert 'John' == get_field(row, 'displayName')
        assert 'John' == get_field(row, 'column-2')
        assert 'John' == get_field(row, 'column-3')
    def test_derive_fields_from_sr(self):
        sr = FakeUser.select()
        d = dict(value=sr)
        self.grid.update_params(d)
        get_field = d['get_field']
        assert ['userId', 'name'] == d['collist']
        row = FakeUser(userId=123, name='john')
        assert 123 == get_field(row, 'userId')
        assert 'john' == get_field(row, 'name')
