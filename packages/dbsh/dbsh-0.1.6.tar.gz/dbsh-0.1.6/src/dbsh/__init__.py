#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""
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

$Id: __init__.py,v 1.7 2008/09/04 19:02:25 vkuznet Exp $
"""

# Define what gets imported with a 'from dbsh import *'
#__all__ = ['dbshell','dbcmd','dbprint','ipy_profile_dbsh.py','utils.py']

__author__   = "Valentin Kuznetsov <vkuznet@gmail.com>"
__license__  = "BSD"
__revision__ = 6
__version__  = 0.1


