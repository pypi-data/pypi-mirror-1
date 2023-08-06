# encoding: utf-8

'''schema_manager
'''

__author__ = 'Chris Miles'
__copyright__ = '(c) Chris Miles 2009. All rights reserved.'
__id__ = '$Id$'
__url__ = '$URL$'


# ---- Imports ----

# - Python modules -
import logging
import types

# - SQLAlchemy modules -
import sqlalchemy as SA

# - SchemaBot modules -
from exceptions import SchemaBotError, ChangeAlreadyDefinedError


# ---- Constants ----

# DROP_COLUMN_NOT_SUPPORTED: Engines that do not support dropping a column
DROP_COLUMN_NOT_SUPPORTED = (
    'sqlite'
)


# ---- Globals ----

default_logger = logging.getLogger("schemabot")


# ---- Classes ----

class SchemaChange(object):
    """A SchemaChange object represents the changes to the schema required
    to upgrade to a particular version from the previous version, or to
    downgrade from the existing version to the earlier version.
    
    Schema changes may be specific to a type of database engines (such as
    'postgres', 'mysql', 'sqlite', etc) and schema changes for each engine
    type can be stored.
    
    When schema changes are requested and an engine is specified, the changes
    for that engine are returned if available; if no changes are defined for
    the specified engine then the default schema changes are returned, if any.
    
    SchemaChange logs its upgrade/downgrade activity to a default logger named
    "schemabot".  The
    """
    def __init__(self, logger=default_logger):
        self.log = logger
        
        self.engines = {}   # keyed by engine name, e.g. 'postgres', 'mysql', 'sqlite', etc
    
    def define_change(self, engine_name=None, upgrade=None, downgrade=None):
        """
        `engine_name` : an engine name, such as 'postgres', 'mysql', 'sqlite', etc.
        Or None for an engine-independent change. Defaults to None.
        
        `upgrade` : list of objects representing changes to schema.  An
        empty list means no action is required.  None indicates no action is
        possible for the engine_name and would cause an exception to be raised
        during upgrade.
        
        `downgrade` : list of DDL SQL statements to perform during downgrade to the
        current version.  An empty list means no action is required.  None indicates
        no action is possible for the engine_name and would cause an exception to
        be raised during downgrade.
        
        Change objects can be any of: DDL SQL statement as string; SQLAlchemy Table
        object; SQLAlchemy Sequence object; or SQLAlchemy DDL object.
        """
        if engine_name is None:
            engine_name = '_default_'
        
        if engine_name in self.engines:
            raise ChangeAlreadyDefinedError("Changes are already defined for engine", engine_name)
        
        self.engines[engine_name] = dict(
            upgrade = upgrade,
            downgrade = downgrade,
        )
    
    def get_changeset(self, engine_name):
        changes = self.engines.get(engine_name)
        if changes is None:
            changes = self.engines.get('_default_')
        # TODO: should changes=None raise an error??
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
            elif isinstance(change, SA.schema.Column):
                column = change
                # Create an ALTER TABLE statement; SQLAlchemy won't do this for us,
                #   although it will generate the column definition statement
                #   correctly for the engine dialect, which is the hard part.
                change = SA.DDL('ALTER TABLE "%s" ADD %s' %(column.table.fullname, connection.dialect.schemagenerator(connection.dialect, connection).get_column_specification(column)))
                self.log.info("Schema change is add column with: %s" %change)
                change.execute(bind=connection)
            elif isinstance(change, (SA.schema.SchemaItem, SA.schema.Sequence)):
                self.log.info("Schema change is: %s.create()" %change)
                change.create(bind=connection)
            elif isinstance(change, SA.schema.DDL):
                self.log.info("Schema change is: %s.execute()" %change)
                change.execute(bind=connection)
            else:
                raise SchemaBotError("Invalid schema change object '%s', expecting string or sqlalchemy schema object" %change)
    
    def downgrade(self, connection):
        changeset = self.get_changeset(connection.engine.name)
        changes = changeset.get('downgrade')
        if changes is None:
            raise SchemaBotError("No changes available.")
        
        for change in changes:
            if isinstance(change, types.StringTypes):
                self.log.info("Schema change is: %s" %change)
                connection.execute(SA.text(change))
            elif isinstance(change, SA.schema.Column):
                if connection.engine.name in DROP_COLUMN_NOT_SUPPORTED:
                    self.log.warn("Dropping columns not supported by engine '%s', skipped.", connection.engine.name)
                else:
                    column = change
                    # Create an ALTER TABLE statement; SQLAlchemy won't do this for us,
                    #   although it will generate the column definition statement
                    #   correctly for the engine dialect, which is the hard part.
                    change = SA.DDL('ALTER TABLE "%s" DROP COLUMN "%s"' %(column.table.fullname, column.name))
                    self.log.info("Schema change is drop column with: %s" %change)
                    change.execute(bind=connection)
            elif isinstance(change, (SA.schema.SchemaItem, SA.schema.Sequence)):
                self.log.info("Schema change is: %s.drop()" %change)
                change.drop(bind=connection)
            elif isinstance(change, SA.schema.DDL):
                self.log.info("Schema change is: %s.execute()" %change)
                change.execute(bind=connection)
            else:
                raise SchemaBotError("Invalid schema change object '%s', expecting string or sqlalchemy.schema.Table" %change)
    


class SchemaManager(object):
    """Represents a set of schema versions.
    
    Register schema versions using the register() method.
    
    Version 0 is reserved for the initial state and cannot be
    registered.
    
    Versions must be registered in sequential order, starting
    from 1.
    """
    def __init__(self, logger=default_logger):
        self.log = logger
        
        self._versions = {}
    
    def register(self, version, upgrade=None, downgrade=None, engine_name=None):
        """Register a schema version.
        
        `version` is the version number.  Version numbers must be registered in
        sequential order, starting from 1.  Version 0 is reserved for
        the initial state.
        
        `upgrade` and `downgrade` should be iterables (e.g. lists) containing
        all the changes required for upgrading from the previous version to
        this version, or for downgrading from this version to the next lowest
        version.  Changes can be SQLAlchemy schema objects (e.g. Table objects)
        or SA.schema.DDL objects or strings containing SQL to be executed.
        """
        if version < 0 or not isinstance(version, int):
            raise SchemaBotError("version must be a positive integer")
        if version == 0:
            raise SchemaBotError("version 0 is reserved for the initial state")
        if version > self.highest_version + 1:
            raise SchemaBotError("versions must be registered sequentially")
        
        versionobj = self._versions.setdefault(version, SchemaChange(logger=self.log))
        try:
            versionobj.define_change(engine_name, upgrade, downgrade)
        except ChangeAlreadyDefinedError, err:
            raise ChangeAlreadyDefinedError("Schema version %d has already been defined for engine '%s'" %(version, err[1]))
    
    def get(self, version):
        return self._versions.get(version)
    
    @property
    def highest_version(self):
        version_numbers = self._versions.keys()
        if not version_numbers:
            return 0
        else:
            return max(version_numbers)
    
