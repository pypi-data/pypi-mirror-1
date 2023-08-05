#!/usr/bin/env python
# vim:ts=4:sw=4:et

from storm.store import Store
from storm.properties import Int, Unicode

from unittest import TestCase
from os import path

import unitstorm

insert1_f = 'insert1.sql'
insert2_f = 'insert2.sql'

fixtures_g = path.join(path.dirname(__file__), 'fixtures')

insert1_s = open(path.join(fixtures_g, insert1_f)).read()
insert2_s = open(path.join(fixtures_g, insert2_f)).read()

class TestModel(object):
    __storm_table__ = 'test'
    id = Int(primary = True)
    name = Unicode()

class TestSetUpMTC(unitstorm.ModelTestCase):
    dburi = 'sqlite:///:memory:'
    fixtures = fixtures_g

    teardown = False

    def __init__(self, *args, **kwargs):
        unitstorm.ModelTestCase.__init__(self, *args, **kwargs)
        self.apply_fixture_sql("""
           CREATE TABLE test (
               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
               name VARCHAR
           );""")

class TestTearDownMTC(TestSetUpMTC):
    teardown = True

class OneRow:
    def test_one_row(self):
        "Table exists and contain one row"
        if self.__class__.teardown:
            self.tearDown()
        row = self.store.find(TestModel, TestModel.name == u'test1')
        assert row.count() == 1
        assert row.one().id == 1

class TwoRows:
    def test_two_rows(self):
        "Table exists and contain two row"
        if self.__class__.teardown:
            self.tearDown()
        rows = self.store.find(TestModel, TestModel.name == u'test1').order_by(TestModel.id)
        assert rows.count() == 2
        assert rows[0].id == 1
        assert rows[1].id == 2

class Order:
    def test_order(self):
        "Sql fixtures execution order"
        if self.__class__.teardown:
            self.tearDown()
        row = self.store.find(TestModel, TestModel.name == u'test1')
        assert row.one().id == 1
        row = self.store.find(TestModel, TestModel.name == u'test2')
        assert row.one().id == 2

class MultiOrder:
    def test_multi_order(self):
        "Fixture fixtures execution order"
        if self.__class__.teardown:
            self.tearDown()
        rows = self.store.find(TestModel, TestModel.name == u'test1').order_by(TestModel.id)
        assert rows[0].id == 1
        assert rows[1].id == 2
        rows = self.store.find(TestModel, TestModel.name == u'test2').order_by(TestModel.id)
        assert rows[0].id == 3
        assert rows[1].id == 4

# ------------------------------------------------------

class TestSqlSetUp(TestSetUpMTC, OneRow):
    sql_setup = insert1_s

class TestMultiSqlSetUp(TestSetUpMTC, TwoRows):
    sql_setup = insert1_s, insert1_s

# ------------------------------------------------------

class TestFixtureSetUp(TestSetUpMTC, OneRow):
    fixture_setup = insert1_f

class TestMultiFixtureSetUp(TestSetUpMTC, TwoRows):
    fixture_setup = insert1_f, insert1_f

# ------------------------------------------------------

class TestMultiSqlSetUpOrder(TestSetUpMTC, Order):
    sql_setup = insert1_s, insert2_s

class TestMultiFixtureSetUpOrder(TestSetUpMTC, Order):
    fixture_setup = insert1_f, insert2_f

class TestSetUpOrder(TestSetUpMTC, Order):
    sql_setup = insert1_s
    fixture_setup = insert2_f

class TestMultiSetUpOrder(TestSetUpMTC, MultiOrder):
    sql_setup = insert1_s, insert1_s
    fixture_setup = insert2_f, insert2_f

# ------------------------------------------------------

class TestSqlTearDown(TestTearDownMTC, OneRow):
    sql_teardown = insert1_s

class TestMultiSqlTearDown(TestTearDownMTC, TwoRows):
    sql_teardown = insert1_s, insert1_s

# ------------------------------------------------------

class TestFixtureTearDown(TestTearDownMTC, OneRow):
    fixture_teardown = insert1_f

class TestMultiFixtureTearDown(TestTearDownMTC, TwoRows):
    fixture_teardown = insert1_f, insert1_f

# ------------------------------------------------------

class TestMultiSqlTearDownOrder(TestTearDownMTC, Order):
    sql_teardown = insert1_s, insert2_s

class TestMultiFixtureTearDownOrder(TestTearDownMTC, Order):
    fixture_teardown = insert1_f, insert2_f

class TestTearDownOrder(TestTearDownMTC, Order):
    fixture_teardown  = insert1_f
    sql_teardown  = insert2_s

class TestMultiTearDownOrder(TestTearDownMTC, MultiOrder):
    fixture_teardown  = insert1_f, insert1_f
    sql_teardown  = insert2_s, insert2_s

# ------------------------------------------------------

class TestOnDemaind(unitstorm.ModelTestCase):
    """no fixtures - no objects"""

    dburi = 'sqlite:///:memory:'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_object_on_demaind(self):
        assert not self.__dict__.has_key('_db')
        assert not self.__dict__.has_key('_store')
        self.__class__.__base__.setUp(self)
        assert not self.__dict__.has_key('_db')
        assert not self.__dict__.has_key('_store')
        self.__class__.__base__.tearDown(self)
        assert not self.__dict__.has_key('_db')
        assert not self.__dict__.has_key('_store')
        self.store.flush()
        assert self.__dict__.has_key('_db')
        assert self.__dict__.has_key('_store')

# ------------------------------------------------------

class TestFixturePath(TestCase):
    """properly merging fixture path and name"""
    
    def test_empty(self):
        class EmptyPath(unitstorm.ModelTestCase):
            fixtures = ''
        assert EmptyPath._fixture_name('fixture.sql') == 'fixture.sql'
    
    def test_end_slash(self):
        class SlashPath(unitstorm.ModelTestCase):
            fixtures = './'
        assert SlashPath._fixture_name('fixture.sql') == './fixture.sql'
    
    def test_no_end_slash(self):
        class NoSlashPath(unitstorm.ModelTestCase):
            fixtures = '.'
        assert NoSlashPath._fixture_name('fixture.sql') == './fixture.sql'
