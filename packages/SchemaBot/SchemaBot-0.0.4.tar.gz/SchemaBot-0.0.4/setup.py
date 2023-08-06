from setuptools import setup, find_packages
import sys, os

version = '0.0.4'

setup(name='SchemaBot',
      version=version,
      description="Database schema version control library for SQLAlchemy",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Chris Miles',
      author_email='miles.chris@gmail.com',
      url='',
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
