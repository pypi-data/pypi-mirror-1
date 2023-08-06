# encoding: utf-8

'''schemabot

Database schema version control library for SQLAlchemy.
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2008. All rights reserved.'
__id__ = '$Id: __init__.py 9 2009-05-11 14:30:18Z chris $'
__url__ = '$URL: https://psychofx.com/schemabot/svn/SchemaBot/trunk/schemabot/__init__.py $'


# ---- Imports ----

# - Python modules -
import logging
import types

# - SQLAlchemy modules -
import sqlalchemy as SA


# ---- Globals ----

default_logger = logging.getLogger("schemabot")


# ---- Exceptions ----

class SchemaBotError(Exception):
    pass

class ChangeAlreadyDefined(SchemaBotError):
    pass


# ---- Classes ----

class SchemaChange(object):
    def __init__(self, log=None):
        if log is None:
            log = default_logger
        self.log = log
        
        self.engines = {}   # keyed by engine name, e.g. 'postgres', 'mysql', 'sqlite', etc
    
    def define_change(self, engine_name=None, upgrade=None, downgrade=None):
        """
        `engine_name` : an engine name, such as 'postgres', 'mysql', 'sqlite', etc.
        Or None for an engine-independent change. Defaults to None.
        
        `upgrade` : list of DDL SQL statements to perform during upgrade to the
        current version.  An empty list means no action is required.  None indicates
        no action is possible for the engine_name and would cause an exception to
        be raised during upgrade.
        
        `downgrade` : list of DDL SQL statements to perform during downgrade to the
        current version.  An empty list means no action is required.  None indicates
        no action is possible for the engine_name and would cause an exception to
        be raised during downgrade.
        """
        if engine_name is None:
            engine_name = '_default_'
        
        if engine_name in self.engines:
            raise ChangeAlreadyDefined("Changes are already defined for engine", engine_name)
        
        self.engines[engine_name] = dict(
            upgrade = upgrade,
            downgrade = downgrade,
        )
    
    def get_changeset(self, engine_name):
        changes = self.engines.get(engine_name)
        if changes is None:
            changes = self.engines.get('_default_')
        if changes is None:
            raise SchemaBotError("No changes available.")
        
        return changes
    
    def upgrade(self, connection):
        changeset = self.get_changeset(connection.engine.name)
        changes = changeset.get('upgrade')
        if changes is None:
            raise SchemaBotError("No changes available.")
        
        for change in changes:
            if isinstance(change, types.StringTypes):
                self.log.info("Schema change is: %s" %change)
                connection.execute(SA.text(change))
            elif isinstance(change, (SA.schema.SchemaItem, SA.schema.Sequence)):
                self.log.info("Schema change is: %s.create()" %change)
                change.create(bind=connection)
            else:
                raise SchemaBotError("Invalid schema change object '%s', expecting string or sqlalchemy schema object")
    
    def downgrade(self, connection):
        changeset = self.get_changeset(connection.engine.name)
        changes = changeset.get('downgrade')
        if changes is None:
            raise SchemaBotError("No changes available.")
        
        for change in changes:
            if isinstance(change, types.StringTypes):
                self.log.info("Schema change is: %s" %change)
                connection.execute(SA.text(change))
            elif isinstance(change, SA.schema.Table):
                self.log.info("Schema change is: %s.drop()" %change)
                change.drop(bind=connection)
            else:
                raise SchemaBotError("Invalid schema change object '%s', expecting string or sqlalchemy.schema.Table")
    
    



class SchemaBot(object):
    def __init__(self, metadata, create_table=True, initial_version=0, log=None):
        """Initialise the SchemaBot SQLAlchemy schema version control mechanism.
        
        Args:
        
        `metadata` : an initialised sqlalchemy.MetaData object that is bound to an
        sqlalchemy engine.
        
        `create_table` : bool indicating whether to automatically create the
        schemabot_version table if it doesn't already exist. Defaults to True.
        
        `initial_version` : version to initialise a newly created schemabot_version
        table to. Defaults to 0.
        
        `log` : a logging.Logger object with methods such as "error", "info", etc.
        Defaults to its own Logger object with context "schemabot".
        """
        if log is None:
            log = default_logger
        self.log = log
        
        self.metadata = metadata
        
        self.schemabot_version_table = SA.Table('schemabot_version', self.metadata,
            # SA.Column('id', SA.Integer, primary_key=True, autoincrement=False),
            SA.Column('current_version', SA.Integer),
        )
        
        if create_table and not self.schemabot_version_table.exists():
            # Create schemabot_version table if it doesn't already exist
            self.schemabot_version_table.create()
            # Initialise the current version (defaults to 0). User can override with `initial_version`
            #   arg in constructor.
            result = self.schemabot_version_table.insert().execute(current_version=initial_version)
            result.close()
        
        self.changes = {}      # keyed by version number; values should be SchemaChange objects
    
    def define_schema(self, version, upgrade=None, downgrade=None, engine_name=None):
        version = int(version)
        if version == 0:
            raise SchemaBotError("Schema version 0 is the initial schema state and cannot contain any schema changes.")
        
        changeobj = self.changes.setdefault(version, SchemaChange(log=self.log))
        try:
            changeobj.define_change(engine_name, upgrade, downgrade)
        except ChangeAlreadyDefined, err:
            raise ChangeAlreadyDefined("Schema version %d has already been defined for engine '%s'" %(version, err[1]))
    
    def get_current_version(self):
        """Fetch the current schema version from the DB (schemabot_version.current_version).
        
        SchemaBotError exception is raised if the version cannot be retrieved, the table
        does not exist, or the data appears to be inconsistent.
        """
        # Check schema version to see if schema updates are required
        try:
            result = self.schemabot_version_table.select().execute().fetchall()
            if len(result) < 1:
                raise SchemaBotError("No version data exists in schemabot_version table.  Call SchemaBot constructor with create_table=True to initialise the table.")
            elif len(result) > 1:
                raise SchemaBotError("schemabot_version table should only contain one row, but %d rows were returned. Cannot continue; please fix manually." %len(result))
            else:
                dbver = result[0][0]
                if type(dbver) != int:
                    raise SchemaBotError("schemabot_version table returned a %s object (value='%s'); expecting an integer. Cannot continue." %(type(dbver), dbver))
        except SA.exceptions.SQLError, err:
            # schemabot_version table does not exist, tell user how to create it manually
            raise SchemaBotError("""SQLError "%s". The schemabot_version table may be missing. If so, try calling the SchemaBot constructor with create_table=True to create and initialise the table.""" %str(err))
        return dbver
    
    def model_version(self, version=None, lowest=False):
        if version is None:
            versions = self.changes.keys()
            if not versions:
                version = 0
            elif lowest:
                version = min(versions)     # smallest version number (excluding 0, the initial version)
            else:
                version = max(versions)     # largest version number
        else:
            version = int(version)          # ensure int
            if version != 0 and not self.changes.get(version):
                raise SchemaBotError("No schema version defined for version %d." %version)
        
        return version
    
    def version_check(self, version=None):
        """Compares the current DB schema version (from schemabot_version.current_version)
        with the version specified (or the maximum defined version if version is None).
        
        Returns a 2-tuple (model_version, current_DB_version)
        """
        model_version = self.model_version(version)
        current_version = self.get_current_version()
        
        return (model_version, current_version)
        
        # # schemabot_version table exists but no results were returned,
        # #   indicating the schema was created by this version of the
        # #   model but no version number has been inserted as yet.
        # if dbver == []:
        #     dbver = SchemaVersion(current_version=schema_version, id=0)
        #     session.flush()
        # 
        # else:
        #     dbver = dbver[0]
        # 
        # current_version = dbver.current_version
        
        # if current_version is None:
        #     current_version = 0
        
        # if model_version > current_version:
        #     # schema upgrade required
        #     return 1
        # elif model_version < current_version:
        #     # schema downgrade required
        #     return -1
        # else:
        #     # versions match
        #     return 0
    
    def schema_update(self, version=None):
        """Upgrade or downgrade the DB schema to match the maximum (upgrade) or
        minimum (downgrade) defined versions; or to the explicit version if
        the `version` argument is specified.
        
        Specify version 0 to downgrade all schema changes.  Version 0 is always
        the initial schema state.
        
        All changes are performed within a transaction, so if any fails the
        whole lot will be rolled back.  i.e. The schema change will be all or
        nothing.  With the exception of the note below.
        
        NOTE: some databases (and/or adaptors) do not support CREATE/DROP/etc within
        a transaction, so those operations cannot be rolled back.  In those cases, the
        database may be left in an inconsistent state if an error occurs during upgrade
        or downgrade.
        Ref http://groups.google.com/group/sqlalchemy/msg/7756ba6582336f54
        """
        model_version = self.model_version(version)     # version to update to
        current_version = self.get_current_version()    # current DB version
        
        if model_version == current_version:
            self.log.info("Live schema version (%d) matches model version (%d)" %(current_version, model_version))
        else:
            if model_version > current_version:
                action = 'upgrade'      # informative only
                start_version = current_version + 1
                stop_version = model_version + 1
                version_step = +1
            else:
                action = 'downgrade'    # informative only
                start_version = current_version
                stop_version = model_version
                version_step = -1
            
            self.log.warn("Live schema version (%d) differs from model version (%d)" %(current_version, model_version))
            engine_name = self.metadata.bind.name
            self.log.warn("Beginning automatic DB schema %s (engine='%s')"%(action,engine_name))
            # Wrap the whole schema update in a transaction.  If any statement
            #   fails the whole update should be rolled back (i.e. no schema
            #   changes will persist).
            #   This will be a sub-transaction if the session was created as
            #   transactional.
            connection = self.metadata.bind.connect()
            trans = connection.begin()
            # session.begin()
            try:
                for version in range(start_version, stop_version, version_step):
                    self.log.warn("Applying schema %s for version: %d" %(action,version))
                    changeobj = self.changes.get(version)
                    if changeobj is None:
                        self.log.error("No schema changes defined for version=%d", version)
                        raise SchemaBotError("No schema changes defined for version=%d"%version)
                    
                    if model_version > current_version:
                        # changes = changeobj.get_upgrade_change(engine_name)
                        changeobj.upgrade(connection)
                    else:
                        # changes = changeobj.get_downgrade_change(engine_name)
                        changeobj.downgrade(connection)
                    
                    # for change in changes:
                    #     if isinstance(change, types.StringTypes):
                    #         self.log.info("Schema change is: %s" %change)
                    #         connection.execute(SA.text(change))
                    #     elif isinstance(change, SA.schema.Table):
                    #         self.log.info("Schema change is: %s.create()" %change)
                    #         change.create() # TODO: downgrade = drop()
                    #     else:
                    #         raise SchemaBotError("Invalid schema change object '%s', expecting string or sqlalchemy.schema.Table")
                
                connection.execute(self.schemabot_version_table.update(), current_version=model_version)
                trans.commit()
            except:
                trans.rollback()
                raise
            
            self.log.warn("Automatic DB schema update complete.  Live schema is now at version %d" %model_version)
        
        # elif current_version < model_version:
        #     raise Exception("TODO")
        # else:
        #     log.info("DEBUG: Live schema version (%d) matches model version (%d)" %(current_version, model_version))



# ---- Module Functions ----

# def define_schema_version_table(metadata):
#     '''Returns an SQLAlchemy Table representation of the
#     schemabot_version table.
#     '''
#     return SA.Table('schemabot_version', metadata,
#         SA.Column('id', SA.Integer, primary_key=True, autoincrement=False),
#         SA.Column('current_version', SA.Integer),
#     )


# def schema_version_check(schema_version, session, metadata, log=None):
#     '''Check the database schema version against the specified version.
#     Returns True if the schema matches or False otherwise (i.e. schema upgrade
#     required).
#     
#     If a schema upgrade is required the user should call schema_upgrade().
#     
#     `schema_version` is an integer and is compared against the
#     schemabot_version.current_version field.
#     
#     `schema_changes` is a dict of schema changes as raw SQL (e.g.
#     CREATE/ALTER/etc statements).  Each key represents a schema version
#     as an integer.  Values are either lists or dicts.  If value is a dict,
#     the key is a database type (e.g. 'postgres', 'mysql', etc) and value is
#     lists of strings, one for each SQL statement, which will be executed in
#     list order.
#     
#     `session` is a session instance created from an SQLAlchemy Session
#     object.
#     
#     `metadata` is a SQLAlchemy metadata object.
#     
#     `log` is a logging.Logger object with methods such as "error", "info", etc.
#     Defaults to its own Logger object with context "sa_schema_ver".
#     
#     The caller must map SchemaVersion to the schemabot_version table.
#     
#     Example::
#         schema_version_table = define_schema_version_table(metadata)
#         Session.mapper(SchemaVersion, schema_version_table)
#     '''
#     if log is None:
#         log = default_logger
#     
#     # Check schema version to see if schema updates are required
#     try:
#         dbver = SchemaVersion.query().all()
#     except SA.exceptions.SQLError, err:
#         # schemabot_version table does not exist, tell user how to create it manually
#         raise SchemaBotError("""SQLError "%s". Database may contain no schema version. Database schema needs to be updated. If your database tables have already been created then you need to create the schemabot_version table manually with:
# CREATE TABLE schemabot_version (
#     id INTEGER NOT NULL, 
#     current_version INTEGER, 
#     PRIMARY KEY (id)
# );
# INSERT INTO schemabot_version (id, current_version) VALUES (0, 0);
# """ %str(err))
# 
#     # schemabot_version table exists but no results were returned,
#     #   indicating the schema was created by this version of the
#     #   model but no version number has been inserted as yet.
#     if dbver == []:
#         dbver = SchemaVersion(current_version=schema_version, id=0)
#         session.flush()
#     
#     else:
#         dbver = dbver[0]
#     
#     current_version = dbver.current_version
#     
#     if current_version is None:
#         current_version = 0
#     if current_version != schema_version:
#         # schema upgrade/downgrade required
#         return False
#     else:
#         # schema version matches
#         return True
    

# def schema_upgrade(schema_version, schema_changes, session, metadata, log=None):
#     """
#     
#     `schema_changes` is a dict of schema changes as raw SQL (e.g.
#     CREATE/ALTER/etc statements).  Each key represents a schema version
#     as an integer.  Values are either lists or dicts.  If value is a dict,
#     the key is a database type (e.g. 'postgres', 'mysql', 'sqlite', etc; matched
#     from engine.name) and value is
#     lists of strings, one for each SQL statement, which will be executed in
#     list order.
#     
#     """
#     if log is None:
#         log = default_logger
#     
#     if current_version > schema_version:
#         log.error("Live schema version (%d) differs from model version (%d)" %(current_version, schema_version))
#         log.error("Beginning automatic DB schema updates")
#         # Wrap the whole schema update in a transaction.  If any statement
#         #   fails the whole update should be rolled back (i.e. no schema
#         #   changes will persist).
#         #   This will be a sub-transaction if the session was created as
#         #   transactional.
#         session.begin()
#         for version in range(current_version+1, schema_version+1):
#             log.error("Applying schema updates for version: %d" %version)
#             for change in schema_changes[version]:
#                 log.info("DEBUG: Schema change is: %s" %change)
#                 session.execute(SA.text(change, bind=metadata.bind))
#         dbver.current_version = schema_version
#         session.commit()
#         if session.transactional:
#             # commit the outer transaction if it was implicitly created
#             session.commit()
#         
#         log.error("Automatic DB schema update complete.  Live schema is now at version %d" %schema_version)
#     elif current_version < schema_version:
#         raise Exception("TODO")
#     else:
#         log.info("DEBUG: Live schema version (%d) matches model version (%d)" %(current_version, schema_version))
# 
