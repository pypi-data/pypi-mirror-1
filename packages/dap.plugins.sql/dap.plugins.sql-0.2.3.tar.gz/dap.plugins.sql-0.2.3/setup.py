# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.2.3'

setup(name='dap.plugins.sql',
      version=version,
      description="SQL plugin for pydap server",
      long_description="""\
This plugin should work with any database module that conforms with the
Python DB-API 2 specification:

    http://www.python.org/peps/pep-0249.html

You can find a list of database modules here:

    http://www.python.org/topics/database/modules.html

It currently has been tested with SQLite, MySQL and PostgreSQL, but it
also should work with Oracle, MSSQL and ODBC.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/plugins/dap_plugin_sql#egg=dap_plugin_sql-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='sql dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/plugins/sql.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap', 'dap.plugins'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'dap[server]>=2.2.6.4',
          'coards>=0.2.2',
      ],
      extras_require={
          'sqlite': ['pysqlite'],
          'postgresql': ['psycopg2'],
          'mysql': ['MySQL-python'],
          'oracle': ['cx_Oracle'],
          'mssql': ['adodbapi'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [dap.plugin]
      main = dap.plugins.sql
      """,
      )
      
