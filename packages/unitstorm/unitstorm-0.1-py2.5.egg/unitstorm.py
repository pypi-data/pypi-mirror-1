#! /usr/bin/env python
# vim:ts=4:sw=4:et

'''
Unit testing microframework for Storm ORM models.

Simple usage:

    import models as model # models define somewhere else
    from unitstorm import ModelTesCase
    
    class TestMyModel(ModelTestCase):
        dburi = 'postgres://test:test@localhost/test'

        sql_setup = 'INSERT INTO my_model (id, name) VALUES (1, "foo");'
        sql_teardown = 'DELETE FROM my_model WHERE id = 1;'

        def test_stub(self):
            assert self.store.get(model.MyModel, 1).name == "foo"

Copyright (c) 2007-2008 Vsevolod S. Balashov under terms of GNU LGPL v.2.1

TODO more docstrings
'''

__author__ = "Vsevolod Balashov"
__email__ = "vsevolod at balashov dot name"
#TODO __version__ = "$Revision$"

from unittest import TestCase
from storm.store import Store
from storm.database import create_database
from os import path

__all__ = ["ModelTestCase"]

class ModelTestCase(TestCase):
    """Base class for model unit tests.
    """
    
    @property
    def db(self):
        """On demaind create and return database connection.
        """
        try:
            return self._db
        except AttributeError:
            self._db = create_database(self.__class__.dburi)
            return self._db
    
    @property
    def store(self):
        """On demaind create and return Store object instance.
        May be override it in base class of functional (controller) testcases.
        
        In middlestorm powered web application obtain Store instance from environ['storm.store'] variable.
        """
        try:
            return self._store
        except AttributeError:
            self._store = Store(self.db)
            return self._store
    
    def _rollback(self):
        try:
            self._store.rollback()
        except AttributeError:
            pass
    
    def apply_fixture_sql(self, sql):
        self.store.execute(sql, noresult = True)
        self.store.commit()
    
    @classmethod
    def _fixture_name(cls, file_name):
        return path.join(cls.fixtures, file_name)
    
    def _apply_fixture(self, file_name):
        self.apply_fixture_sql(open(self._fixture_name(file_name)).read())
    
    def each_fixture(self, name):
        try:
            fixture = self.__class__.__dict__[name]
            if type(fixture) is tuple:
                for f in fixture:
                    yield f
            else:
                yield fixture
        except KeyError:
            pass
    
    def setUp(self):
        TestCase.setUp(self)
        self._rollback()
        for fixture_sql in self.each_fixture('sql_setup'):
            self.apply_fixture_sql(fixture_sql)
        for fixture in self.each_fixture('fixture_setup'):
            self._apply_fixture(fixture)
    
    def tearDown(self):
        self._rollback()
        for fixture in self.each_fixture('fixture_teardown'):
            self._apply_fixture(fixture)
        for fixture_sql in self.each_fixture('sql_teardown'):
            self.apply_fixture_sql(fixture_sql)
        TestCase.tearDown(self)
