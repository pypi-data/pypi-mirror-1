from setuptools import setup, find_packages
import sys, os

execfile(os.path.join(os.path.dirname(__file__), 'schemabot', 'version.py'))

setup(
    name='SchemaBot',
    version=version,
    description="Python package to automatically manage database schema version control when using SQLAlchemy. Databases can be easily upgraded or downgraded to any version of the schema.",
    long_description="""\
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
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
