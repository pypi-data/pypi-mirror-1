# encoding: utf-8

'''schemabot

Database schema version control library for SQLAlchemy.
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2008. All rights reserved.'
__id__ = '$Id$'
__url__ = '$URL$'


# ---- Imports ----

# - Python modules -
import logging

# - SQLAlchemy modules -
import sqlalchemy as SA

# - SchemaBot modules -
from exceptions import SchemaBotError


# ---- Globals ----

default_logger = logging.getLogger("schemabot")


# ---- Classes ----

class SchemaBot(object):
    def __init__(self, schema_mgr, engine=None, create_table=True,
                initial_version=0, logger=default_logger):
        """Initialise the SchemaBot SQLAlchemy schema version control
        mechanism.
        
        Args:
        
        `schema_mgr` : An instance of schemabot.SchemaManager containing
        all the registered schema versions.
        
        `engine` : an SQLAlchemy engine that SchemaBot will use to make
        connections to the database.  If create_table is True then an
        engine must be specified.
        
        `create_table` : bool indicating whether to automatically create
        the schemabot_version table if it doesn't already exist. Defaults
        to True.
        
        `initial_version` : version to initialise a newly created
        schemabot_version table to. Defaults to 0.
        
        `logger` : a logging.Logger object with methods such as "error",
        "info", etc. Defaults to its own Logger object with context
        "schemabot".
        """
        self.log = logger
        
        self.schema_mgr = schema_mgr
        self.engine = engine
        
        metadata = SA.MetaData()
        
        self.schemabot_version_table = SA.Table('schemabot_version', metadata,
            SA.Column('current_version', SA.Integer),
        )
        
        if create_table:
            try:
                table_exists = self.schemabot_version_table.exists(bind=engine)
            except SA.exc.UnboundExecutionError:
                raise SchemaBotError("SchemaBot cannot auto create the schemabot_version table without an engine to bind to.")
            
            if not table_exists:
                # Create schemabot_version table if it doesn't already exist
                self.schemabot_version_table.create(bind=engine)
                # Initialise the current version (defaults to 0). User can override with `initial_version`
                #   arg in constructor.
                result = self.schemabot_version_table.insert(bind=engine).execute(current_version=initial_version)
                result.close()
    
    def get_current_version(self, bind=None):
        """Fetch the current schema version from the DB (schemabot_version.current_version).
        
        SchemaBotError exception is raised if the version cannot be retrieved, the table
        does not exist, or the data appears to be inconsistent.
        """
        if bind is not None:
            engine = bind
        else:
            engine = self.engine
        
        if engine is None:
            raise SchemaBotError("SchemaBot has no engine to bind to; try the 'bind' argument to get_current_version().")
        
        # Check schema version to see if schema updates are required
        try:
            result = self.schemabot_version_table.select(bind=engine).execute().fetchall()
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
        """Return a valid model version number.
        
        If version is None and lowest is False (the defaults) then the
        highest registered model version number is returned.
        
        If version is None and lowest is True then 0 is returned.
        
        If version is an integer then it will be returned if it matches
        a valid registered version number; otherwise a SchemaBotError
        exception is raised.
        """
        if version is None:
            if lowest:
                version = 0
            else:
                version = self.schema_mgr.highest_version
        else:
            version = int(version)          # ensure int
            if version != 0 and not self.schema_mgr.get(version):
                raise SchemaBotError("No schema version defined for version %d." %version)
        
        return version
    
    def version_check(self, version=None, bind=None):
        """Compares the current DB schema version (from schemabot_version.current_version)
        with the version specified (or the maximum defined version if version is None).
        
        Returns a 2-tuple (model_version, current_DB_version)
        """
        if bind is not None:
            engine = bind
        else:
            engine = self.engine
        
        if engine is None:
            raise SchemaBotError("SchemaBot has no engine to bind to; try the 'bind' argument to version_check().")
        
        model_version = self.model_version(version)
        current_version = self.get_current_version(bind=engine)
        
        return (model_version, current_version)
    
    def schema_update(self, version=None, bind=None):
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
        if bind is not None:
            engine = bind
        else:
            engine = self.engine
        
        if engine is None:
            raise SchemaBotError("SchemaBot has no engine to bind to; try the 'bind' argument to schema_update().")
        
        model_version = self.model_version(version)             # version to update to
        current_version = self.get_current_version(bind=engine) # current DB version
        
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
            self.log.warn("Beginning automatic DB schema %s (engine='%s')"%(action,engine.name))
            
            # Wrap the whole schema update in a transaction.  If any statement
            #   fails the whole update should be rolled back (i.e. no schema
            #   changes will persist).
            #   This will be a sub-transaction if the session was created as
            #   transactional.
            connection = engine.connect()
            trans = connection.begin()
            try:
                for version in range(start_version, stop_version, version_step):
                    self.log.warn("Applying schema %s for version: %d" %(action,version))
                    changeobj = self.schema_mgr.get(version)
                    if changeobj is None:
                        self.log.error("No schema changes defined for version=%d", version)
                        raise SchemaBotError("No schema changes defined for version=%d"%version)
                    
                    if model_version > current_version:
                        changeobj.upgrade(connection)
                    else:
                        changeobj.downgrade(connection)
                
                connection.execute(self.schemabot_version_table.update(), current_version=model_version)
                trans.commit()
            except:
                trans.rollback()
                raise
            
            self.log.warn("Automatic DB schema update complete.  Live schema is now at version %d" %model_version)
    
    def drop_schemabot_tables(self, bind=None, checkfirst=True):
        """Ask SchemaBot to drop any tables that it automatically creates.
        Currently, this is just the "schemabot_version" table.
        
        Pass an engine object with the `bind` parameter, if one wasn't
        passed to the constructor.
        
        If `checkfirst` is True (the default) then SchemaBot will first
        check whether the table exists and only drop if it needs to.
        If False, it will attempt to drop it unconditionally which may
        raise an exception if the table doesn't exist.
        """
        if bind is not None:
            engine = bind
        else:
            engine = self.engine
        
        if engine is None:
            raise SchemaBotError("SchemaBot has no engine to bind to; try the 'bind' argument to drop_schemabot_tables().")
        
        if not checkfirst or (checkfirst and self.schemabot_version_table.exists(bind=engine)):
            self.schemabot_version_table.drop(bind=engine)
    
