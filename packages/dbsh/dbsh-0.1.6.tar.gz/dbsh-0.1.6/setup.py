#!/usr/bin/env python

import os, sys
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from sys import version
from src import dbsh

if sys.version_info < (2, 4):
    raise Exception("dbsh requires Python 2.4 or higher.")

scriptfiles=filter(os.path.isfile, ['bin/dbsh'])
setup(
    name = "dbsh",
    version = "%s.%s"%(dbsh.__version__,dbsh.__revision__),
    description = "Common, interactive, programmable environment and simple shell to connect and manipulate your favorite DB content",
    package_dir = {'dbsh':'src/dbsh'},
    data_files = [('config',['src/config/ipythonrc'])],
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    scripts = scriptfiles,
    long_description = """\

dbsh -- an interactive shell for DB back-end.

Every known DB has its own shell for SQL operations.
The dbshell (dbsh) provides unique, interactive, programmable environment
and simple shell to connect and manipulate your favorite DB contexts. 
It supports naturally a syntax of DB you use to, for example, while you connect to
MySQL dbsh supports full syntax of MySQL, but when you connect to ORACLE it supports
ORALCE SQL and commands.

It is based on two components:
- interactive python IPython, http://ipython.scipy.org/moin/About.
- SQLAlchemy, http://www.sqlalchemy.org

It uses SQLAlchemy ORB tool as an SQL layer to perform interactive operations against given DB-backend.
Therefore it provides common shell for ANY DB back-end in uniform fashion.
All SQL operations supported by given DB back-end naturally supported by dbsh.

""",
    classifiers = [
        'Environment :: Console',
        "Intended Audience :: Developers",
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: BSD License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends",
    ],

    dependency_links = ['http://www.sqlalchemy.org/','http://ipython.scipy.org/moin/About'],
    install_requires=["IPython", "SQLAlchemy"],
#    dependency_links = ['http://www.sqlalchemy.org/','http://ipython.scipy.org/moin/About','http://numpy.scipy.org/','http://matplotlib.sourceforge.net/'],
#    install_requires=["IPython", "SQLAlchemy","numpy","matplotlib"],
    author = "Valentin Kuznetsov",
    author_email = "dbsh4u@gmail.com",
    url = "http://www.dbshell.org",
    license = "BSD License",
)

