SchemaBot
=========

Automatically manages SQLAlchemy database schema upgrades/downgrades.

See tests for examples of how to use it.

Run tests with::

  nosetests

By default, tests are performed against an in-memory sqlite database ('sqlite://').

To run tests against a specific database, set the SCHEMABOT_TEST_DBURI environment
variable to the database URI.  Some examples::

  $ SCHEMABOT_TEST_DBURI=postgres://localhost/test1 nosetests
  $ SCHEMABOT_TEST_DBURI=sqlite:///mytest.db nosetests
