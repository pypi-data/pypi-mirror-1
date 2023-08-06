#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################

cmdDict = {
 "connect":"Invoke connection to DB",
 "close":"Close connection to DB",
 "dbhelp":"dbsh help",
 "rerun":"Re-run command",
 "select":"Execute select SQL statement",
 "insert":"Execute insert SQL statement",
 "drop":"Execute drop SQL statement, in particular we support drop database or drop tables <table_name>",
 "update":"Execute update SQL statement",
 "create":"Execute create SQL statement",
 "alter":"Execute aleter SQL statement",
 "show":"Show information about DB, e.g. show tables",
 "desc":"Print table description",
 "dump":"Dump content of DB",
# "page":"Set pagination",
 "migrate":"Migrate content of current DB into another one",
 "mydb":"List all known (connected) DBs",
 "set":"Execute set SQL statement",
 "rollback":"Execute rollback SQL statement",
 "begin":"Execute begin SQL statement",
 "commit":"Execute commit SQL statement",
 "explain":"Execute explain SQL statement",
 "source":"Execute SQL from external file",
 "format":"Set-up formatting output",
}
cmdDictExt = {
 "connect":"""
Invoke connection to DB via the following connector

       driver://username:password@host:port/database:owner

The following parameters are optional: host, port, owner. Below you can find all examples.
 MySQL   mysql://user:password@localhost:port/dbname
         mysql://user:password@localhost/dbname,
 ORACLE  oracle://user:password@dns/dbname (use ORACLE TNS service)
         oracle://user:password@127.0.0.1:1521/sidname,
 SQLite  sqlite:////absolute/path/to/database.txt
         sqlite:///relative/path/to/database.txt,
""",
 "close":"Close connection to DB. Once you connected to DB you may wish to close this connection. The close support both syntax via driver or db alias. For full list of known db aliases see mydb command",
 "dbhelp":"dbsh help. It support optional parameter to give you comprehensive help about given keyword, e.g. dbhelp connect will print out extended version of help section for 'connect' keyword.",
 "rerun":"Re-run command corresponding to given number, e.g. rerun 5 will rerun 5th command from history.",
 "select":"""
Execute select statement, dbsh accepts a full SQL syntax appropriate for given DB back-end.
SQL ANSI support the following select statments:

        SELECT expression_list
        FROM data_source
        WHERE predicates
        GROUP BY expression_list
        HAVING predicates
        ORDER BY expression_list

""",
 "insert":"""
Execute insert SQL statement, dbsh accepts a full SQL syntax appropriate for given DB back-end.
SQL ANSI support the following insert statments:

        INSER INTO table_name
        (column_list)
        VALUES
        (value list matched columnt_list)

""",
 "drop":"""
Execute insert SQL statement, dbsh accepts a full SQL syntax appropriate for given DB back-end.
Please use you DB vendor documentation to see if it support DROP statement. But dbsh support at
least two command. One is to drop one table:

        DROP TABLE table_name

And another is to drop all tables in connected database via the following statement:

        DROP DATABASE

""",
 "update":"""
Execute update SQL statement, dbsh accepts a full SQL syntax appropriate for given DB back-end.
SQL ANSI support the following update statments:

        UPDATE TABLE table_name
        SET column_name = value, column_name = value, ...
        WHERE predicates

""",
 "create":"""
Execute create SQL statement, dbsh accepts a full SQL syntax appropriate for given DB back-end.
You can create new table in a database by issuing CREATE TABLE statement. The syntax varies widely
among vendors. Please consult your DB back-end documentation. Here we illustrate a reasonable
example:

        CREATE TABLE table_name (
            id INTEGER,
            name VARCHAR(10),
            timestamp DATE
        );

""",
 "alter":"""
Execute aleter SQL statement, dbsh accepts a full SQL syntax appropriate for given DB back-end.
We support DB back-end syntax which varies among vendors. In general the ALTER command is the
following:

        ALTER TABLE table_name
        ADD COLUMN column_name <column_type>
        ADD CONSTRAIN constrain_name CHECK(condition)
        ..........................
        ALTER COLUMN column_name SET <new data type or assign default, etc.>
        ..........................
        DROP CONSTRAIN constrain_name

""",
 "show":"Show information about DB, e.g. show tables shows all found tables in connected DB",
 "desc":"Prints out table description",
 "dump":"Dump content of DB",
# "page":"Set pagination, support one or two arguments. Example page <offset> <limit>",
 "migrate":"Migrate content of current DB into another one",
 "mydb":"List all known (connected) DBs",
 "set":"""
Execute set SQL statement. Varios DB vendors use SET command for different purposes, mainly to setup transactions. For exact syntax please consult your DB vendor documentation.
""",
 "rollback":"""
Execute rollback SQL statement. In most cases the ROLLBACK statement has been used in transaction content to rollback current transaction. For exact syntax please consult your DB vendor documentation.
""",
 "begin":"""Execute begin SQL statement. In most cases the BEGIN statement indicates start of transaction. For exact syntax please consult your DB vendor documentation.
""",
 "commit":"""Execute commite SQL statement. In most cases the COMMIT statement indicates commitment of current transaction. For exact syntax please consult your DB vendor documentation.
""",
 "explain":"""Execute explain SQL statement. For exact syntax please consult your DB vendor documentation. Here is basic usage:

        EXPLAIN select * from Table;

""",
 "source":"""Execute SQL from external file, e.g. source file.sql, where file.sql contains a set of SQL statements.""",
 "format":"""Set-up formatting output. We support the following formats: txt, html, xml, csv (comma separating values). Once you issue this command the underlyin format will be used for all subsequentive queries. 
""",
}
