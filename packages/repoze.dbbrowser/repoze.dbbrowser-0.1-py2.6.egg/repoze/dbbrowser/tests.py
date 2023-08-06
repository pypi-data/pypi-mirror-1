import unittest

from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Column
from sqlalchemy import Table

from repoze.bfg import testing
from repoze.bfg.configuration import Configurator

from repoze.dbbrowser.dbbrowser import Base
from repoze.dbbrowser.dbbrowser import DBSession

class MyModel(Base):
    __tablename__ = 'mymodel'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

def setup_db():
    db_string = 'sqlite:///:memory:'
    engine = create_engine(db_string)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    session = DBSession()
    for i in range(21):
        model = MyModel(name=u'test name %d' % i,value=i*5)
        session.add(model)
        session.commit()
    return session

def cleanup_db(session):
    session.query(MyModel).delete()
    session.commit()
    session.close()

class TestViews(unittest.TestCase):

    def setUp(self):
        self.config = Configurator()
        self.config.begin()
        self.config.add_static_view('static','static')
        self.session = setup_db()

    def tearDown(self):
        self.config.end()
        cleanup_db(self.session)

    def test_main_view(self):
        from repoze.dbbrowser.views import dbbrowser_view
        renderer = self.config.testing_add_template('templates/dbbrowser.pt')
        request = testing.DummyRequest()
        response = dbbrowser_view(request)
        self.assertEqual(response['static_url'], 'http://example.com/static')
        self.assertEqual(response['theme_switcher'], False)
        self.assertEqual(response['tables'][0]['name'], 'mymodel')
        self.assertEqual(len(response['tables']), 1)

    def test_tabledata_view_default(self):
        from repoze.dbbrowser.views import tabledata_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        response = tabledata_view(request)
        self.assertEqual(response['page'], 1)
        self.assertEqual(response['total'], 3)
        self.assertEqual(response['records'], 21)
        self.assertEqual(response['rows'][0]['cell'], (1,u'test name 0',0))
        self.assertEqual(response['rows'][9]['cell'], (10,u'test name 9',45))
        self.assertEqual(len(response['rows']), 10)

    def test_tabledata_view_page(self):
        from repoze.dbbrowser.views import tabledata_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['page'] = '2'
        response = tabledata_view(request)
        self.assertEqual(response['page'], 2)
        self.assertEqual(response['total'], 3)
        self.assertEqual(response['records'], 21)
        self.assertEqual(response['rows'][0]['cell'], (11,u'test name 10',50))
        self.assertEqual(response['rows'][9]['cell'], (20,u'test name 19',95))
        self.assertEqual(len(response['rows']), 10)

    def test_tabledata_view_last(self):
        from repoze.dbbrowser.views import tabledata_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['page'] = '3'
        response = tabledata_view(request)
        self.assertEqual(response['page'], 3)
        self.assertEqual(response['total'], 3)
        self.assertEqual(response['records'], 21)
        self.assertEqual(response['rows'][0]['cell'], (21,u'test name 20',100))
        self.assertEqual(len(response['rows']), 1)

    def test_tabledata_view_sort(self):
        from repoze.dbbrowser.views import tabledata_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['page'] = '1'
        request.params['sidx'] = 'name'
        request.params['sord'] = 'desc'
        response = tabledata_view(request)
        self.assertEqual(response['page'], 1)
        self.assertEqual(response['total'], 3)
        self.assertEqual(response['records'], 21)
        self.assertEqual(response['rows'][0]['cell'], (10,u'test name 9',45))
        self.assertEqual(response['rows'][9]['cell'], (20,u'test name 19',95))
        self.assertEqual(len(response['rows']), 10)

    def test_tabledata_view_search(self):
        from repoze.dbbrowser.views import tabledata_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['page'] = '1'
        request.params['_search'] = 'true'
        request.params['searchField'] = 'name'
        request.params['searchString'] = '9'
        request.params['searchOper'] = 'cn'
        response = tabledata_view(request)
        self.assertEqual(response['page'], 1)
        self.assertEqual(response['total'], 1)
        self.assertEqual(response['records'], 2)
        self.assertEqual(response['rows'][0]['cell'], (10,u'test name 9',45))
        self.assertEqual(response['rows'][1]['cell'], (20,u'test name 19',95))
        self.assertEqual(len(response['rows']), 2)

    def test_tableedit_view_add(self):
        from repoze.dbbrowser.views import tableedit_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['oper'] = 'add'
        request.params['name'] = u'add test name'
        request.params['value'] = u'88'
        response = tableedit_view(request)
        entries = self.session.query(MyModel).count()
        new_entry = self.session.query(MyModel).filter(MyModel.id==22).all()
        self.assertEqual(entries, 22)
        self.assertEqual(len(new_entry), 1)
        self.assertEqual(new_entry[0].name, u'add test name')
        self.assertEqual(new_entry[0].value, 88)

    def test_tableedit_view_edit(self):
        from repoze.dbbrowser.views import tableedit_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['oper'] = 'edit'
        request.params['name'] = u'edit test name'
        request.params['value'] = u'55'
        request.params['id'] = u'2'
        response = tableedit_view(request)
        entries = self.session.query(MyModel).count()
        new_entry = self.session.query(MyModel).filter(MyModel.id==2).all()
        self.assertEqual(entries, 21)
        self.assertEqual(len(new_entry), 1)
        self.assertEqual(new_entry[0].name, u'edit test name')
        self.assertEqual(new_entry[0].value, 55)

    def test_tableedit_view_delete(self):
        from repoze.dbbrowser.views import tableedit_view
        request = testing.DummyRequest()
        request.params['table'] = 'mymodel'
        request.params['oper'] = 'del'
        request.params['id'] = u'1'
        response = tableedit_view(request)
        entries = self.session.query(MyModel).count()
        empty = self.session.query(MyModel).filter(MyModel.id==1).count()
        self.assertEqual(entries, 20)
        self.assertEqual(empty, 0)

