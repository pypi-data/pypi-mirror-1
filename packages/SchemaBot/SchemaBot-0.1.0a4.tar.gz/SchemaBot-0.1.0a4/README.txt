SchemaBot
=========

Automatically manages SQLAlchemy database schema upgrades/downgrades.

Documentation is still being written.  See `docs/tutorial.txt`. If
you are using Pylons see `docs/schemabot-with-pylons.txt`.
Also see Notes below and don't forget the unit tests.

Run tests with::

  nosetests

By default, tests are performed against an in-memory sqlite database
('sqlite://').

To run tests against a specific database, set the SCHEMABOT_TEST_DBURI
environment variable to the database URI.  Some examples::

  $ SCHEMABOT_TEST_DBURI=postgres://localhost/test1 nosetests
  $ SCHEMABOT_TEST_DBURI=sqlite:///mytest.db nosetests



Notes
-----

* Defining a schema change for version 0 is prohibited.  Version 0 is
  reserved for the initial state of the schema (typically an empty
  schema).  Downgrading to version 0 is always possible, which should
  take the schema back to the initial state, before any schema changes.

* Attempting to define schema changes for a version and engine that
  already have a defined change is prohibited.
