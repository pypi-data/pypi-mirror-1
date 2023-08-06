#!/usr/bin/env python
# encoding: utf-8
"""
test_schemabot.py

Created by Chris Miles on 2009-02-03.
Copyright (c) 2009 Chris Miles. All rights reserved.
"""

import os
import unittest

import nose

import sqlalchemy as SA
from sqlalchemy import orm

from schemabot import SchemaBot, SchemaChange, SchemaBotError, ChangeAlreadyDefined


# Only some database engines support table CREATE/DROP/etc within
#   a transaction.  Those that do not cannot have CREATE/DROP/etc
#   rolled back, which is a shame.  The databases that do not
#   support it are listed here so that the relevant rollback tests
#   can be skipped.
# Ref http://groups.google.com/group/sqlalchemy/msg/7756ba6582336f54
CREATE_TABLE_TRANSACTIONAL_NOT_SUPPORTED = [
    'sqlite'
]


class TestSchemaBot(unittest.TestCase):
    def _init_db(self, dburi):
        self.engine = SA.create_engine(dburi)
        self.metadata = SA.MetaData()
        self.metadata.bind = self.engine
    
    def _enable_logging(self):
        import logging, sys
        log = logging.getLogger("schemabot")
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.StreamHandler(sys.stdout))
        self.metadata.bind.echo = True
    
    def _drop_all_tables(self):
        # Try to ensure that we drop all remaining tables from the DB.
        #   This doesn't matter for in-memory databases ('sqlite://') that
        #   will be re-initialised for the next test, but is important
        #   for testing database servers (like postgresql) where the
        #   test database won't be destroyed and re-created for each test.
        
        # Reflect some manually created tables that may still exist
        manually_created_tables = ['test1', 'test2', 'test3']
        for t in manually_created_tables:
            try:
                SA.Table(t, self.metadata, autoload=True)
            except SA.exceptions.NoSuchTableError:
                # import traceback; print traceback.format_exc()  # DEBUG
                pass
        
        # Drop all tables that have been registered with the metadata
        # which should include manually created tables now that they
        # have been reflected
        self.metadata.drop_all()
    
    def setUp(self):
        dburi = os.environ.get("SCHEMABOT_TEST_DBURI")
        if dburi is None:
            dburi = 'sqlite://'
            # dburi = 'postgres://localhost/test1'
        
        self._init_db(dburi)
        self._enable_logging()
    
    def tearDown(self):
        self._drop_all_tables()
        self.metadata.clear()
    
    def test_schemabot_initialise_default(self):
        schemabot = SchemaBot(self.metadata)
        self.failUnlessEqual(type(schemabot), SchemaBot)
        
        result = schemabot.schemabot_version_table.select().execute().fetchall()
        self.failUnlessEqual(len(result), 1)
        self.failUnlessEqual(result[0][0], 0)
    
    def test_schemabot_initialise_create_table_initial_version(self):
        schemabot = SchemaBot(self.metadata, create_table=True, initial_version=5)
        self.failUnlessEqual(type(schemabot), SchemaBot)
        
        result = schemabot.schemabot_version_table.select().execute().fetchall()
        self.failUnlessEqual(len(result), 1)
        self.failUnlessEqual(result[0][0], 5)
    
    def test_schemabot_initialise_no_create_table(self):
        schemabot = SchemaBot(self.metadata, create_table=False)
        self.failUnlessEqual(type(schemabot), SchemaBot)
        
        self.failUnlessEqual(schemabot.schemabot_version_table.exists(), False)
    
    def test_schemabot_define_schema_default(self):
        schemabot = SchemaBot(self.metadata)
        upgrade=[
            """CREATE TABLE test1 (
                foo         char(5),
                bar         varchar(40) NOT NULL,
                zip         integer NOT NULL,
                )
            """
        ]
        downgrade = [
            """DROP TABLE test1"""
        ]
        schemabot.define_schema(1, upgrade=upgrade, downgrade=downgrade, engine_name=None)
        
        self.failUnlessEqual(len(schemabot.changes), 1)
        self.failUnlessEqual(type(schemabot.changes[1]), SchemaChange)
        self.failUnlessEqual(len(schemabot.changes[1].engines), 1)
        self.failUnlessEqual(type(schemabot.changes[1].engines.get('_default_')), dict)
    
    def test_schemabot_define_schema_postgres(self):
        schemabot = SchemaBot(self.metadata)
        upgrade=[
            """CREATE TABLE test1 (
                foo         char(5),
                bar         varchar(40) NOT NULL,
                zip         integer NOT NULL,
                )
            """
        ]
        downgrade = [
            """DROP TABLE test1"""
        ]
        schemabot.define_schema(1, upgrade=upgrade, downgrade=downgrade, engine_name='postgres')
        
        self.failUnlessEqual(len(schemabot.changes), 1)
        self.failUnlessEqual(type(schemabot.changes[1]), SchemaChange)
        self.failUnlessEqual(len(schemabot.changes[1].engines), 1)
        self.failUnlessEqual(schemabot.changes[1].engines.get('_default_'), None)
        self.failUnlessEqual(type(schemabot.changes[1].engines.get('postgres')), dict)
    
    def test_schemabot_define_schema_multi_engines(self):
        schemabot = SchemaBot(self.metadata)
        upgrade=[
            """CREATE TABLE test1 (
                foo         char(5),
                bar         varchar(40) NOT NULL,
                zip         integer NOT NULL,
                )
            """
        ]
        downgrade = [
            """DROP TABLE test1"""
        ]
        schemabot.define_schema(1, upgrade=upgrade, downgrade=downgrade, engine_name='postgres')
        schemabot.define_schema(1, upgrade=upgrade, downgrade=downgrade, engine_name='mysql')
        schemabot.define_schema(1, upgrade=upgrade, downgrade=downgrade, engine_name=None)
        
        self.failUnlessEqual(len(schemabot.changes), 1)
        self.failUnlessEqual(type(schemabot.changes[1]), SchemaChange)
        self.failUnlessEqual(len(schemabot.changes[1].engines), 3)
        self.failUnlessEqual(type(schemabot.changes[1].engines.get('postgres')), dict)
        self.failUnlessEqual(type(schemabot.changes[1].engines.get('mysql')), dict)
        self.failUnlessEqual(type(schemabot.changes[1].engines.get('_default_')), dict)
        self.failUnlessEqual(schemabot.changes[1].engines.get('sqlite'), None)
    
    def test_schemabot_define_version_0(self):
        schemabot = SchemaBot(self.metadata)
        self.failUnlessRaises(SchemaBotError, schemabot.define_schema, 0, upgrade=[], downgrade=[])
    
    def test_schemabot_duplicate_version_engine(self):
        schemabot = SchemaBot(self.metadata)
        schemabot.define_schema(1, upgrade=[], downgrade=[], engine_name='postgres')
        self.failUnlessRaises(ChangeAlreadyDefined, schemabot.define_schema, 1, upgrade=[], downgrade=[], engine_name='postgres')
    
    def test_schemabot_get_current_version_default(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 0)
    
    def test_schemabot_get_current_version_explicit(self):
        schemabot = SchemaBot(self.metadata, create_table=True, initial_version=1)
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 1)
    
    def test_schemabot_no_versions_defined(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        (model_version, current_DB_version) = schemabot.version_check()
        self.failUnlessEqual(model_version, 0)
        self.failUnlessEqual(current_DB_version, 0)
    
    def test_schemabot_version_check_initial_state(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        (model_version, current_DB_version) = schemabot.version_check(0)
        self.failUnlessEqual(model_version, current_DB_version) # versions equal
    
    def test_schemabot_version_check_upgrade(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=[], downgrade=[], engine_name=None)
        (model_version, current_DB_version) = schemabot.version_check()
        self.failUnlessEqual(model_version > current_DB_version, True) # requires upgrade
        
        (model_version, current_DB_version) = schemabot.version_check(version=0)     # check against explicit version
        self.failUnlessEqual(model_version == current_DB_version, True) # versions equal
    
    def test_schemabot_version_check_downgrade(self):
        schemabot = SchemaBot(self.metadata, create_table=True, initial_version=5)      # DB version = 5
        schemabot.define_schema(1, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(2, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(3, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(4, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(5, upgrade=[], downgrade=[], engine_name=None)
        (model_version, current_DB_version) = schemabot.version_check()
        self.failUnlessEqual(model_version, current_DB_version) # versions equal
        
        (model_version, current_DB_version) = schemabot.version_check(version=4)     # check against explicit version
        self.failUnlessEqual(model_version < current_DB_version, True) # requires downgrade
        
        (model_version, current_DB_version) = schemabot.version_check(version=5)     # check against explicit version
        self.failUnlessEqual(model_version, current_DB_version) # versions equal
    
    def test_schema_update_upgrade_empty_changes(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(2, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(3, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(4, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(5, upgrade=[], downgrade=[], engine_name=None)
        
        schemabot.schema_update()
        
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 5)
    
    def test_schema_update_upgrade_downgrade_empty_changes(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(2, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(3, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(4, upgrade=[], downgrade=[], engine_name=None)
        schemabot.define_schema(5, upgrade=[], downgrade=[], engine_name=None)
        
        schemabot.schema_update()
        schemabot.schema_update(version=0)
        
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 0)
    
    def test_schema_update_sql_error(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=["CREATE TABLE test1 (foo INTEGER)"], downgrade=[], engine_name=None)
        schemabot.define_schema(2, upgrade=["CREATE TABLE test1 (foo INTEGER)"], downgrade=[], engine_name=None)
        
        self.failUnlessRaises(
            (SA.exceptions.OperationalError, SA.exceptions.ProgrammingError),
            schemabot.schema_update
        )
    
    def test_schema_update_sql_error_rollback(self):
        if self.metadata.bind.name in CREATE_TABLE_TRANSACTIONAL_NOT_SUPPORTED:
            raise nose.SkipTest
        
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=["CREATE TABLE test1 (foo INTEGER)"], downgrade=[], engine_name=None)
        schemabot.define_schema(2, upgrade=["CREATE TABLE test1 (foo INTEGER)"], downgrade=[], engine_name=None)
        
        self.failUnlessRaises(
            (SA.exceptions.OperationalError, SA.exceptions.ProgrammingError),
            schemabot.schema_update
        )
        # Try to reflect the test1 table, which should fail (the CREATE should be rolled back)
        self.failUnlessRaises(SA.exceptions.NoSuchTableError, SA.Table, 'test1', self.metadata, autoload=True)
    
    def test_schema_update_upgrade(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=["CREATE TABLE test1 (foo INTEGER)"])
        schemabot.define_schema(2, upgrade=["CREATE TABLE test2 (bar INTEGER)"])
        
        schemabot.schema_update()
        
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 2)
    
    def test_schema_update_upgrade_downgrade(self):
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=["CREATE TABLE test1 (foo INTEGER)"], downgrade=["DROP TABLE test1"])
        schemabot.define_schema(2, upgrade=["CREATE TABLE test2 (bar INTEGER)"], downgrade=["DROP TABLE test2"])
        
        # upgrade
        schemabot.schema_update()
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 2)
        
        # downgrade
        schemabot.schema_update(version=0)
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 0)
    
    def test_schema_update_sa_table(self):
        test1_table = SA.Table("test1", self.metadata,
            SA.Column('id', SA.types.Integer),
            SA.Column("pool_id", SA.types.Integer),
        )
        SA.Index('idx_test1_id_pool_id', test1_table.c.id, test1_table.c.pool_id)
        
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=[test1_table])
        
        schemabot.schema_update()
        
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 1)
        
        self.failUnlessEqual(test1_table.exists(), True)
    
    def test_schema_update_upgrade_downgrade_sa_table(self):
        test2_table = SA.Table("test2", self.metadata,
            SA.Column('id', SA.types.Integer),
            SA.Column("pool_id", SA.types.Integer),
        )
        SA.Index('idx_test2_id_pool_id', test2_table.c.id, test2_table.c.pool_id)
        
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=[test2_table], downgrade=[test2_table])
        
        # Upgrade
        schemabot.schema_update()
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 1)
        self.failUnlessEqual(test2_table.exists(), True)
        
        # Downgrade
        schemabot.schema_update(0)
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 0)
        self.failUnlessEqual(test2_table.exists(), False)
    
    def test_schema_update_sa_table_rollback(self):
        if self.metadata.bind.name in CREATE_TABLE_TRANSACTIONAL_NOT_SUPPORTED:
            raise nose.SkipTest
        
        test1_table = SA.Table("test1", self.metadata,
            SA.Column('id', SA.types.Integer),
            SA.Column("pool_id", SA.types.Integer),
        )
        SA.Index('idx_test1_id_pool_id', test1_table.c.id, test1_table.c.pool_id)
        
        schemabot = SchemaBot(self.metadata, create_table=True)
        schemabot.define_schema(1, upgrade=[test1_table])
        schemabot.define_schema(2, upgrade=["BROKEN"])
        
        self.failUnlessRaises(
            (SA.exceptions.OperationalError, SA.exceptions.ProgrammingError),
            schemabot.schema_update
        )
        
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 0)
        
        self.failUnlessEqual(test1_table.exists(), False)
    
    def test_schema_update_sa_sequence(self):
        # test1_seq = SA.Sequence("test1seq", start=100)
        test1_seq = SA.Sequence("test1seq", self.metadata)
        schemabot = SchemaBot(self.metadata)
        schemabot.define_schema(1, upgrade=[test1_seq])
        
        schemabot.schema_update()
        
        result = schemabot.get_current_version()
        self.failUnlessEqual(result, 1)
        
        result = self.engine.execute(test1_seq)
        
        if result is None:
            # On some database engines, Sequences are allowed but
            #   silently ignored.
            raise nose.SkipTest
        
        # self.failUnlessEqual(result, 100)
        self.failUnlessEqual(result, 1L)
    



if __name__ == '__main__':
    unittest.main()
