#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""
DB Shell class and utilities
"""

import os, sys, string, time, types, traceback
from dbsh.dbcmd import *
from dbsh.dbprint import *
from dbsh.utils import *

#from sqlalchemy import *
import sqlalchemy
#from sqlalchemy.databases import information_schema
from sqlalchemy.databases import oracle
from sqlalchemy.databases import mysql
from sqlalchemy.databases import sqlite

# QueryBuilder
#from QueryBuilder.WriteSqlAlchemyGraph import WriteSqlAlchemyGraph
#from QueryBuilder.DotGraph import DotGraph

class DBManager(object):
  """
     DBSDD class takes care of authentication with underlying DB using
     DBS_DBPARAM. SQLAlchemy to provides DB access layer, currently I added
     SQLite, MySQL, ORACLE support. The tables automatically retrieves from DB
     and internal schema can be reconstructed on the fly.

     For description of SQLAlchemy pleasee see
     http://www.sqlalchemy.org
                                
  """
  def __init__(self,verbose=0):
      """
         DBSDD constructor. 
         @type verbose: boolean or integer
         @param verbose: verbosity level
         @rtype : none
         @return: none
      """
      self.verbose   = verbose
      self.printMgr  = PrintOutput()
      self.printMethod = "txt"
      self.tCache    = []
      self.clear()

  def clear(self):
      self.engine    = {}
      self.dbTables  = {}
      self.dbType    = {}
      self.dbOwner   = {}
      self.dbSchema  = {}
      self.metaDict  = {}
      self.con       = None
      self.limit     = None
      self.offset    = None
      self.drivers   = {}
      self.aliases   = {}
      self.query     = ""
      self.result    = ""
      
#  def writeGraph(self,dbAlias):
#      print "writeGraph"
#      fileName="%s.dot"%dbAlias
#      dot=DotGraph(file(fileName,"w"))
#      tDict = self.dbTables[dbAlias]
#      for key in tDict.keys():
#          table=tDict[key]
#          tableName=key
#          foreignKeys=table.foreign_keys
#          for fk in foreignKeys:
#              right=fk.column.table.name
#              if right!='person': # exclude person table
#                 dot.AddEdge(tableName,right)
#      dot.Finish()

  def dbname(self,arg):
      if self.drivers.has_key(arg):
         arg = self.drivers[arg]
      dbType,dbName,dbUser,dbPass,host,port,owner,fileName=self.parse(arg)
      if dbType.lower()=='oracle': return "%s-%s-%s |\#> "%(dbType,owner,dbName)
      if dbType.lower()=='mysql': return "%s-%s-%s |\#> "%(dbType,dbName,host)
      if dbType.lower()=='sqlite': 
         f = fileName.split("/")[-1]
         return "%s-%s |\#> "%(dbType,f)
      return "%s-%s |\#> "%(dbType,dbName)

  def showTable(self,dbAlias):
      if  self.dbTables.has_key(dbAlias):
          tables = self.dbTables[dbAlias].keys()
          tables.sort()
          self.printList(tables,"\nFound tables")
      else:
          self.printList([],"\nFound tables")

  def showDB(self):
      print "Show DB content"
      
  def plot(self,dbAlias,query):
      import pylab
      try:
          result = self.con.execute(query)
      except:
          raise traceback.print_exc()
      xList  = []
      yList  = []
      for item in result:
          if type(item) is types.StringType:
              raise item+"\n"
          if not tList:
             tList=list(item.keys())
          if len(item)!=2:
             raise "Plot support only 2-dimensional data"
          x,y = item
          xList.append(x)
          yList.append(y)
      pylab.plot(xList,yList)
      pylab.show()
      
  def desc(self,dbAlias,table):
      tables = self.dbTables[dbAlias]
      tabObj = tables[table]
      print tabObj
      tList = ['Name','Type','Key','Default','Autoincrment','Foreign Keys']
      oList = [] # contains tuple of values for tList
      lList = [len(x) for x in tList] # column width list
      for col in tabObj.columns:
          key   = ""
          if col.unique: key="unique"
          elif col.primary_key: key="primary"
          value = "NULL"
          if col.default: value = col.default
          foreignKeys=""
          for fk in col.foreign_keys:
              foreignKeys+="%s "%fk.column
          vList = (col.name,col.type,key,value,col.autoincrement,foreignKeys)
          oList.append(vList)
          for idx in xrange(0,len(vList)):
              if lList[idx]<len(str(vList[idx])): lList[idx]=len(str(vList[idx]))
      oList.sort() 
      self.printTable(tList,oList,lList)

  def dump(self,dbAlias,fileName=None):
      tables = self.dbTables[dbAlias]
      dbType = self.dbType[dbAlias]
      msg    = "--\n-- Dump %s.\n-- %s\n"%(dbAlias,makeTIME(time.time()))
      if  fileName:
          file= open(fileName,'w') 
          file.write(msg)
      else:
          print msg
      for tName in tables.keys():
          table = tables[tName]
          try:
             table.create()
          except:
             error = sys.exc_info()[1]
             if  fileName:
                 file.write("%s;\n"%error.statement)
             else:
                 print "%s;\n"%error.statement
          try:
              result = self.con.execute("SELECT * FROM %s"%tName)
              for item in result:
                  if type(item) is types.StringType:
                      raise item+"\n"
                  columns = str(item.keys()).replace("[","(").replace("]",")")
                  values  = str(item.values()).replace("[","(").replace("]",")")
                  stm = "INSERT INTO %s %s VALUES %s;"%(tName,columns,values)
                  if  fileName:
                      file.write(stm+"\n")
                  else:
                      print stm
          except:
              raise traceback.print_exc()
      if fileName:
         file.close()

  def migrate(self,dbAlias,arg):
      tables = self.dbTables[dbAlias]
      dbCon  = self.con
      self.connect(arg)
      newDBAlias = self.aliases[arg]
      remoteEngine = self.engine[newDBAlias]
      meta = sqlalchemy.MetaData()
      meta.bind = remoteEngine
      for table in tables.keys():
          tables[table].create(bind=remoteEngine)
          newTable = tables[table].tometadata(meta)
          query = "select * from %s"%table
          try:
              result = dbCon.execute(query)
          except:
              raise traceback.print_exc()
          con = remoteEngine.connect()
          for item in result:
              if type(item) is types.StringType:
                  raise item+"\n"
              ins = newTable.insert(values=item.values())
              con.execute(ins)
          con.close()
      print "The content of '%s' has been successfully migrated to '%s'"%(dbAlias,newDBAlias)
      print "You may invoke "+self.printMgr.msgGREEN("connect %s"%arg)+" command now."
      self.close(newDBAlias)

  def createAlias(self,name,params):
      self.dbalias[name]=params

  def page(self,arg):
      iList = arg.split()
      if  len(iList)==2:
          self.offset= int(iList[0])
          self.limit = int(iList[1])
      elif len(iList)==1:
          self.limit = int(iList[0])
          self.offset= 0
      else:
          msg="ERROR: page support only one or two arguments"
          msg+= cmdDictExt['page']+"\n"
          raise msg+"\n"

  def next(self):
      self.offset+=self.limit
      if len(self.tCache)>self.offset:
         result = self.tCache[self.offset:self.offset+self.limit]
      else:
         result = self.result
      self.printResult(result,self.query)

  def prev(self):
      self.offset-=self.limit
      if self.offset<0:
         return
      result = self.tCache[self.offset:self.offset+self.limit]
      self.printResult(result,self.query)

  def execute(self,dbAlias,query,listResults=1):
      self.tCache=[]
      self.query=query
      try:
          result = self.con.execute(query)
          self.result = result
      except:
          raise traceback.print_exc()
      if not listResults: return
      self.printResult(result,query)

  def printResult(self,result,query):
      oList  = []
      tList  = []
      lList  = []
      # NEW
      if self.limit and not (type(result) is types.ListType):
         result = fetchFromTo(result,self.limit,self.offset)
      # END OF NEW
      for item in result:
          if type(item) is types.StringType:
             raise item+"\n"
          if not (type(result) is types.ListType):
             self.tCache.append(item)
          if not tList:
             tList=list(item.keys())
             lList=[len(x) for x in tList]
          vList = item.values()
          oList.append(vList)
          for idx in xrange(0,len(vList)):
              if lList[idx]<len(str(vList[idx])): lList[idx]=len(str(vList[idx]))
      self.printTable(tList,oList,lList,query)

  def dropDB(self,dbAlias):
      tables = self.dbTables[dbAlias]
      for tName in tables.keys():
          table = tables[tName]
          try:
             table.drop()
          except:
             traceback.print_exc()
      self.dbTables.pop(dbAlias)

  def dropTable(self,dbAlias,tableName):
      tables = self.dbTables[dbAlias]
      if tables.has_key(tableName):
         tables.pop(tableName)

  def reconnect(self,dbAlias,reloadTables=None):
      self.con.close()
      self.con = self.engine[dbAlias].connect()
      if reloadTables:
         self.dbTables = {}
      self.loadTables(dbAlias)

  def close(self,dbAlias):
      self.con.close()
      for dict in ['engine','dbTables','dbType','metaDict','drivers']:
          getattr(self,dict).pop(dbAlias)
      
  def parse(self,arg):
      """ 
         SQLAlchemy support the following format driver://username:password@host:port/database,
         while here we extend it to the following structure (suitable for ORACLE)
         driver://username:password@host:port/database:dbOwner
      """
      port = None
      host = None
      owner= None
      fileName = None
      dbName = None
      dbUser = None
      dbPass = None
      try:
          driver, dbparams = arg.split("://")
      except:
          msg = "Fail to parse connect argument '%s'\n"%arg
          msg+= cmdDictExt['connect']
          raise msg+"\n"
      if  dbparams.find("@")!=-1:
          user_pass, rest  = dbparams.split("@")
          dbUser,dbPass    = user_pass.split(":")
          if  rest.find("/")!=-1:
              host_port, dbrest= rest.split("/")
              try:
                  host, port = host_port.split(":") 
              except:
                  host = host_port
                  pass
          else:
              dbrest = rest
          try:
              dbName, owner  = dbrest.split(":")
          except:
              dbName = dbrest
              pass
      else: # in case of SQLite, dbparams is a file name
          fileName = dbparams
          dbName   = fileName.split("/")[-1]
          if driver!='sqlite':
             msg = "'%s' parameter is not supported for driver '%s'"%(fileName,driver)
             raise msg+"\n"
#      print "driver",driver
#      print "dbName",dbName
#      print "dbUser",dbUser
#      print "dbPass",dbPass
#      print "host",host
#      print "port",port
#      print "owner",owner
#      print "file",fileName
      return (driver.lower(),dbName,dbUser,dbPass,host,port,owner,fileName)

  def connect(self,driver):
      """Connect to DB"""
      if self.drivers.has_key(driver):
         arg = self.drivers[driver]
      else:
         arg = driver
      dbType,dbName,dbUser,dbPass,host,port,dbOwner,fileName = self.parse(arg)
      dbSchema=None
      if dbType =='oracle' and dbOwner:
         dbAlias = dbOwner
         dbSchema= dbOwner.lower()
      else:
         dbAlias = dbName
      if  not self.drivers.has_key(driver):
          self.drivers[dbAlias]=driver
          self.aliases[driver]=dbAlias
      eType  = string.lower(dbType)
      print "Connecting to %s (%s back-end), please wait ..."%(dbAlias,dbType)

      # Initialize SQLAlchemy engines
      if  not self.engine.has_key(dbAlias):
          eName=""
          if eType=='sqlite':
             eName = "%s:///%s"%(eType,fileName)
             engine= sqlalchemy.create_engine(eName)
          elif eType=='oracle':
             eName = "%s://%s:%s@%s"%(eType,dbUser,dbPass,dbName)
             engine= sqlalchemy.create_engine(eName,strategy='threadlocal',threaded=True)
          elif eType=='mysql':
             eName = "%s://%s:%s@%s/%s"%(eType,dbUser,dbPass,host,dbName)
             engine= sqlalchemy.create_engine(eName,strategy='threadlocal')
          else:
             printExcept("Unsupported DB engine back-end")
          self.engine[dbAlias]=engine
      if  not self.dbType.has_key(dbAlias): self.dbType[dbAlias] = eType
      if  not self.dbOwner.has_key(dbOwner): self.dbOwner[dbAlias] = dbOwner
      if  not self.dbSchema.has_key(dbSchema): self.dbSchema[dbAlias] = dbSchema
      self.con = self.engine[dbAlias].connect()
      self.loadTables(dbAlias)
      return self.con

  def loadTables(self,dbAlias):
      dbMeta = sqlalchemy.MetaData()
      dbMeta.bind=self.engine[dbAlias]
      self.metaDict[dbAlias]=dbMeta
      if  self.dbTables.has_key(dbAlias):
          tables = self.dbTables[dbAlias]
      else:
          tables = {}
      eType = self.dbType[dbAlias]
      engine = self.engine[dbAlias]
      if  eType!='oracle':
          tableNames=engine.table_names()
      else:
          query="SELECT table_name FROM all_tables WHERE owner='%s'"%self.dbOwner[dbAlias]
          tableNames=self.con.execute(query)
      for tName in tableNames:
          if tables.has_key(tName): continue
          if eType=='oracle':
             t = tName[0].lower().split(".")[-1]
             print "Loading '%s' table"%t
             tables[t]=sqlalchemy.Table(t,dbMeta,autoload=True,schema=self.dbSchema[dbAlias],oracle_renyms=True,useexisting=True)
          else:
             print "Loading '%s' table"%tName
             tables[tName.lower()]=sqlalchemy.Table(tName.lower(),dbMeta,autoload=True)
      self.dbTables[dbAlias]=tables

  def printTable(self,tList,oList,lList,msg=None):
      if self.printMethod=="txt":
         self.printMgr.printTXT(tList,oList,lList,msg)
      elif self.printMethod=="xml":
         self.printMgr.printXML(tList,oList,lList,msg)
      elif self.printMethod=="html":
         self.printMgr.printHTML(tList,oList,lList,msg)
      elif self.printMethod=="csv":
         self.printMgr.printCSV(tList,oList,lList,msg)
      else:
         self.printMgr.printTXT(tList,oList,lList,msg)

  def printList(self,iList,msg=None):
      if  msg:
          s="-"*len(msg)
          print msg
          print s
      for item in iList:
          print item

  def makeMapper(self,tname,code,caps):
      print """%s = %s
       class %s (object):
          pass
       mapper(%s, %s)
       """ % (tname, code, caps, caps, tname)

  def getForeignKeys(self,dbAlias,table):
      tDict = self.dbTables[dbAlias]
      if self.dbType[dbAlias]=='oracle':
         table=string.upper(table)
      if tDict.has_key(table):
         return tDict[table].foreign_keys
      raise "No table '%s' found"%table+"\n"

#
# main
#
if __name__ == "__main__":
   db = DBManager()
   db.connect('sqlite://test.db')
   db.showTable('test.db')
   db.execute('test.db',"select * from test")
