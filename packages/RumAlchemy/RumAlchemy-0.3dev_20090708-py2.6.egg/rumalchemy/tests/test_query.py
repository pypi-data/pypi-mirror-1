from unittest import TestCase
from sqlalchemy import create_engine, sql
from sqlalchemy.orm import create_session
from rum import query as rumquery
#TODO: Use rumalchemy.tests.model instead and remove that module
from rumalchemy.tests import model2 as model
from rumalchemy.query import translate, SAQuery, _escape_char

class TestTranslate(TestCase):
    def test_eq(self):
        expr = translate(rumquery.eq('name', 'Alberto'), model.Person)
        expected = model.Person.name == 'Alberto'
        self.failUnlessEqual(expected, expr)
    
    def test_neq(self):
        expr = translate(rumquery.neq('name', 'Alberto'), model.Person)
        expected = model.Person.name != 'Alberto'
        self.failUnlessEqual(expected, expr)
    
    def test_contains(self):
        expr = translate(rumquery.contains('name', 'Alberto'), model.Person)
        expected = model.Person.name.contains('Alberto')
        self.failUnlessEqual(expected, expr)

    def test_startswith(self):
        expr = translate(rumquery.startswith('name', 'Alberto'), model.Person)
        expected = model.Person.name.startswith('Alberto')
        self.failUnlessEqual(expected, expr)

    def test_endswith(self):
        expr = translate(rumquery.endswith('name', 'Alberto'), model.Person)
        expected = model.Person.name.endswith('Alberto')
        self.failUnlessEqual(expected, expr)

    def test_lt(self):
        expr = translate(rumquery.lt('name', 'Alberto'), model.Person)
        expected = model.Person.name < 'Alberto'
        self.failUnlessEqual(expected, expr)

    def test_lte(self):
        expr = translate(rumquery.lte('name', 'Alberto'), model.Person)
        expected = model.Person.name <= 'Alberto'
        self.failUnlessEqual(expected, expr)

    def test_gt(self):
        expr = translate(rumquery.gt('name', 'Alberto'), model.Person)
        expected = model.Person.name > 'Alberto'
        self.failUnlessEqual(expected, expr)

    def test_gte(self):
        expr = translate(rumquery.gte('name', 'Alberto'), model.Person)
        expected = model.Person.name >= 'Alberto'
        self.failUnlessEqual(expected, expr)

    def test_not(self):
        expr = translate(rumquery.not_('name'), model.Person)
        expected = not model.Person.name
        self.failUnlessEqual(expected, expr)

    def test_null(self):
        expr = translate(rumquery.null('name'), model.Person)
        expected = model.Person.name == None
        self.failUnlessEqual(expected, expr)

    def test_negated_null(self):
        expr = translate(rumquery.not_(rumquery.null('name')), model.Person)
        expected = model.Person.name != None
        self.failUnlessEqual(expected, expr)

    def test_notnull(self):
        expr = translate(rumquery.notnull('name'), model.Person)
        expected = model.Person.name != None
        self.failUnlessEqual(expected, expr)

    def test_and(self):
        expr = translate(rumquery.and_([
            rumquery.not_(rumquery.null('name')),
            rumquery.gte('name', 'Alberto'),
            rumquery.contains('name', 'Alberto'),
            ]), model.Person)
        expected = (
            (model.Person.name != None) &
            (model.Person.name >= 'Alberto') &
            sql.func.lower(model.Person.name).contains(sql.func.lower('Alberto'),escape=_escape_char)
            )
        # test for string equality here because SA fails to recognize as equal
        # this expr even though they're the same  
        self.failUnlessEqual(str(expected), str(expr))

    def test_or(self):
        expr = translate(rumquery.or_([
            rumquery.not_(rumquery.null('name')),
            rumquery.gte('name', 'Alberto'),
            rumquery.contains('name', 'Alberto'),
            ]), model.Person)
        expected = (
            (model.Person.name != None) |
            (model.Person.name >= 'Alberto') |
            sql.func.lower(model.Person.name).contains(
              sql.func.lower('Alberto'),escape=_escape_char)
            )
            
        # test for string equality here because SA fails to recognize as equal
        # this expr even though they're the same  
        self.failUnlessEqual(str(expected), str(expr))

    def test_in(self):
        expr = translate(rumquery.in_('name', ['Alberto' 'Peter', 'Alba']),
                         model.Person)
        expected = model.Person.name.in_(['Alberto', 'Peter', 'Alba'])
        self.failUnlessEqual(expected, expr)

class TestSAQuery(TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        model.Model.metadata.create_all(bind=self.engine)

    def tearDown(self):
        model.Model.metadata.drop_all(bind=self.engine)

    def makeSession(self):
       return create_session(bind=self.engine, autoflush=True,
                             autocommit=True)

    def test_filtering(self):
        test_data = [
            model.Person(name=u'Albaricoque'),
            model.Person(name=u'Peter'),
            model.Person(name=u'Lucy'),
            model.Person(name=u'Alba'),
            ]
        session = self.makeSession()
        map(session.add, test_data)
        session.flush()
        session.expunge_all()

        q = session.query(model.Person)
        query = SAQuery(rumquery.startswith('name', 'A'), resource=model.Person)
        items = list(query.filter(q))
        self.failUnlessEqual(len(items), 2)
        self.failUnlessEqual(query.count, 2)

    def test_sorting(self):
        test_data = [
            model.Person(name=u'Albaricoque', age=23),
            model.Person(name=u'Peter', age=32),
            model.Person(name=u'Lucy', age=19),
            model.Person(name=u'Albino', age=23),
            ]
        session = self.makeSession()
        map(session.add, test_data)
        session.flush()
        session.expunge_all()

        q = session.query(model.Person)
        query = SAQuery(sort=[rumquery.asc('age'), rumquery.asc('name')],
                        resource=model.Person)
        names = [p.name for p in query.filter(q)]
        expected = ["Lucy", "Albaricoque", "Albino", "Peter"]
        self.failUnlessEqual(names, expected)

    def test_pagination(self):
        test_data = [
            model.Person(name=u'Albaricoque', age=23),
            model.Person(name=u'Peter', age=32),
            model.Person(name=u'Lucy', age=19),
            model.Person(name=u'Albino', age=23),
            ]
        session = self.makeSession()
        map(session.add, test_data)
        session.flush()
        session.expunge_all()

        q = session.query(model.Person)
        query = SAQuery(sort=[rumquery.asc('age'), rumquery.asc('name')],
                        limit=2,
                        offset=0,
                        resource=model.Person)
        names = [p.name for p in query.filter(q)]
        expected = ["Lucy", "Albaricoque"]
        self.failUnlessEqual(names, expected)

        q = session.query(model.Person)
        query = SAQuery(sort=[rumquery.asc('age'), rumquery.asc('name')],
                        limit=2,
                        offset=2,
                        resource=model.Person)
        names = [p.name for p in query.filter(q)]
        expected = ["Albino", "Peter"]
        self.failUnlessEqual(names, expected)
