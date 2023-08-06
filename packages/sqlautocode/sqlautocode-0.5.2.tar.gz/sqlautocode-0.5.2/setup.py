#!python
# -*- coding: UTF-8 -*-

"""
Setup script for building sqlautocode
"""

version = open('version.txt').next().strip()

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

DOC = """
This is a tool that helps you creating a model based on an existing database scheme. The resulting code will be compatible with sqlalchemy.

Installation::

    easy_install sqlautocode
    $PYTHON/bin/sqlautocode

Example::

    sqlautocode postgres://user:password@myhost/database -o out.py -t person*,account

Options::

      -h, --help            show this help message and exit
      -o OUTPUT, --output=OUTPUT
                            Write to file (default is stdout)
      --force               Overwrite file (default is stdout)
      -s SCHEMA, --schema=SCHEMA
                            Optional, reflect a non-default schema
      -t TABLES, --tables=TABLES
                            Optional, only reflect this comma-separated list of
                            tables. Wildcarding with '*' is supported, e.g:
                            --tables account_*,orders,order_items,*_audit
      -i, --noindexes, --noindex
                            Do not emit index information
      -g, --generic-types   Emit generic ANSI column types instead of database-
                            specific.
      --encoding=ENCODING   Encoding for output, default utf8
      -e, --example         Generate code with examples how to access data (outdated)
      -3, --z3c             Generate code for use with z3c.sqlalchemy

For more information and sourcecode go to: http://code.google.com/p/sqlautocode/

"""

setup (name = 'sqlautocode',
		version = version,
		description = 'AutoCode is a flexible tool to autogenerate a model from an existing database.',
        long_description=DOC,
		author = 'Simon Pamies',
		author_email = 'spamsch@gmail.com',
		maintainer = 'Simon Pamies',
		maintainer_email = 'spamsch@gmail.com',
		url = 'http://code.google.com/p/sqlautocode/',
        platforms=['Unix', 'Windows'],
		packages = find_packages(exclude=['ez_setup', 'tests']),
		zip_safe=True,
		license = 'MIT',
		classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"Programming Language :: Python",
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
		],
		entry_points = dict(
			console_scripts = [
				'sqlautocode = sqlautocode:main',
			],
		),
        install_requires=[
            'sqlalchemy>=0.5'
        ],
		tests_require=[
			'nose>=0.10',
		],
		test_suite = "nose.collector",
	)
