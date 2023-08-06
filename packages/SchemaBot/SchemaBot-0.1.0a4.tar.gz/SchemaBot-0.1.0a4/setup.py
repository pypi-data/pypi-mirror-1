from setuptools import setup, find_packages
import sys, os

execfile(os.path.join(os.path.dirname(__file__), 'schemabot', 'version.py'))

setup(
    name='SchemaBot',
    version=version,
    description="Python package to automatically manage database schema version control when using SQLAlchemy. Databases can be easily upgraded or downgraded to any version of the schema.",
    long_description="""\
Quick SchemaBot Tutorial
========================

Define your initial model and register as schema version 1::

  >>> import sqlalchemy as SA
  >>> from schemabot import SchemaBot, SchemaManager
  >>> meta = SA.MetaData()
  >>> user_table = SA.Table("user", meta,
  ...     SA.Column('id', SA.types.Integer),
  ...     SA.Column('username', SA.types.Unicode),
  ...     SA.Column('password', SA.types.Unicode),
  ... )
  >>> default_admin_user = "INSERT INTO user (id, username, password) VALUES (1, 'admin', 'admin')"
  >>> schema_version_1_upgrade = [user_table, default_admin_user]
  >>> schema_version_1_downgrade = [user_table]
  >>> schema_mgr = SchemaManager()
  >>> schema_mgr.register(1, upgrade=schema_version_1_upgrade, downgrade=schema_version_1_downgrade)
  
  >>> engine = SA.create_engine('sqlite:///test1.db')
  
  >>> schemabot = SchemaBot(schema_mgr, engine=engine, create_table=True)
  >>> (model_version, current_db_version) = schemabot.version_check()
  >>> print (model_version, current_db_version)
  (1, 0)
  >>> if model_version != current_db_version:
  ...     schemabot.schema_update()
  
  >>> print schemabot.get_current_version()
  1


In another terminal (don't close the above Python session) examine
the resulting database::

  $ sqlite3 test1.db
  Loading resources from /Users/chris/.sqliterc
  SQLite version 3.4.0
  Enter ".help" for instructions
  sqlite> .tables
  schemabot_version  user             
  sqlite> .schema user
  CREATE TABLE user (
          id INTEGER, 
          username VARCHAR, 
          password VARCHAR
  );
  sqlite> SELECT * FROM schemabot_version;
  current_version
  ---------------
  1
  sqlite> SELECT * FROM user;
  id          username    password  
  ----------  ----------  ----------
  1           admin       admin


Return to the existing Python session, define schema version 2 and upgrade::

  >>> address_table = SA.Table('address', meta,
  ...     SA.Column('id', SA.types.Integer),
  ...     SA.Column('user_id', SA.types.Integer, SA.ForeignKey('user.id')),
  ...     SA.Column('street', SA.types.Unicode),
  ...     SA.Column('city', SA.types.Unicode),
  ... )
  >>> schema_version_2 = [address_table]
  >>> schema_mgr.register(2, upgrade=schema_version_2, downgrade=schema_version_2)
  >>> (model_version, current_db_version) = schemabot.version_check()
  >>> print (model_version, current_db_version)
  (2, 1)
  >>> if model_version != current_db_version:
  ...     schemabot.schema_update()
  
  >>> print schemabot.get_current_version()
  2

In another terminal, examine the database::

  $ sqlite3 test1.db
  Loading resources from /Users/chris/.sqliterc
  SQLite version 3.4.0
  Enter ".help" for instructions
  sqlite> .tables
  address            schemabot_version  user             
  sqlite> .schema address
  CREATE TABLE address (
          id INTEGER, 
          user_id INTEGER, 
          street VARCHAR, 
          city VARCHAR, 
           FOREIGN KEY(user_id) REFERENCES user (id)
  );
  sqlite> SELECT * FROM schemabot_version;
  current_version
  ---------------
  2

Return to the existing Python session. Let's downgrade the schema back to
the initial state (version 0).  We will enable SQLAlchemy statement logging
(echo) so we can see the action as it happens::

  >>> engine.echo = True
  >>> schemabot.schema_update(version=0)
  2009-05-27 13:46:08,690 INFO sqlalchemy.engine.base.Engine.0x...9a10 SELECT schemabot_version.current_version 
  FROM schemabot_version
  2009-05-27 13:46:08,691 INFO sqlalchemy.engine.base.Engine.0x...9a10 []
  2009-05-27 13:46:08,691 INFO sqlalchemy.engine.base.Engine.0x...9a10 BEGIN
  2009-05-27 13:46:08,693 INFO sqlalchemy.engine.base.Engine.0x...9a10 
  DROP TABLE address
  2009-05-27 13:46:08,693 INFO sqlalchemy.engine.base.Engine.0x...9a10 ()
  2009-05-27 13:46:08,696 INFO sqlalchemy.engine.base.Engine.0x...9a10 
  DROP TABLE user
  2009-05-27 13:46:08,697 INFO sqlalchemy.engine.base.Engine.0x...9a10 ()
  2009-05-27 13:46:08,699 INFO sqlalchemy.engine.base.Engine.0x...9a10 UPDATE schemabot_version SET current_version=?
  2009-05-27 13:46:08,700 INFO sqlalchemy.engine.base.Engine.0x...9a10 [0]
  2009-05-27 13:46:08,701 INFO sqlalchemy.engine.base.Engine.0x...9a10 COMMIT
  >>> print schemabot.get_current_version()
  2009-05-27 13:47:06,115 INFO sqlalchemy.engine.base.Engine.0x...9a10 SELECT schemabot_version.current_version 
  FROM schemabot_version
  2009-05-27 13:47:06,115 INFO sqlalchemy.engine.base.Engine.0x...9a10 []
  0

Swapping back to look at the database directly::

  $ sqlite3 test1.db 
  Loading resources from /Users/chris/.sqliterc
  SQLite version 3.4.0
  Enter ".help" for instructions
  sqlite> .tables
  schemabot_version
  sqlite> SELECT * FROM schemabot_version;
  current_version
  ---------------
  0

    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='sqlalchemy, database, schema, version, pylons',
    author=author,
    author_email=author_email,
    url='http://bitbucket.org/chrismiles/schemabot/',
    download_url='http://pypi.python.org/pypi/SchemaBot',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        "SQLAlchemy >= 0.4",
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
