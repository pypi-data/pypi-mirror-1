#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################

# system modules
import os, sys, time, types, string, popen2, traceback

# ipython modules
from IPython import Release
import IPython.ipapi
ip = IPython.ipapi.get()

import dbsh
from dbsh.dbshell import *
from dbsh.dbcmd import *
from dbsh.dbprint import *
    
import __main__ 


try:
    db=DBManager()
    dbprint=PrintOutput()
except:
    traceback.print_exc()
    raise "ERROR: fail to load DBManager"

__alias_table__={}
def is_ready():
    if  not db.con:
        print "This function is not available until you connect to DB"
        return 1
    return 0

def setPrompt(in1):
    IP = __main__.__dict__['__IP'] 
    prompt = getattr(IP.outputcache,'prompt1') 
    prompt.p_template = in1
    prompt.set_p_str() 

def getPrompt():
    IP = __main__.__dict__['__IP'] 
    prompt = getattr(IP.outputcache,'prompt1') 
    return IP.outputcache.prompt1.p_template

def dbAlias():
    prompt = getPrompt()
    return prompt.split("|")[0].split("-")[1].strip() # see how dbshell define dbname and dbAlias

def connect(self,arg):
    db.connect(arg)
    setPrompt(db.dbname(arg))

def close(self,arg):
    if is_ready(): return
    db.close(dbAlias())
    setPrompt('dbsh |\#> ')

def rerun(self,arg):
    ip.ex("exec _i%d" % int(arg))

def show(self,arg):
    if is_ready(): return
    if arg=='tables':
       db.showTable(dbAlias())
    else:
       db.execute(dbAlias(),"show "+arg.replace(";",""))
#       print dbprint.msgRED("ERROR: '%s' not supported keyword"%arg)

def desc(self,arg):
    if is_ready(): return
    db.desc(dbAlias(),arg)

def dump(self,arg):
    if is_ready(): return
    db.dump(dbAlias(),arg)

def page(self,arg):
    db.page(arg)

def next(self,arg):
    db.next()

def prev(self,arg):
    db.prev()

def migrate(self,arg):
    if is_ready(): return
    db.migrate(dbAlias(),arg)

def mydb(self,arg):
    if len(db.dbType.keys()):
        _msg="You are connected to the following DBs:"
        msg =_msg+"\n"+"-"*len(_msg)
        print msg
        for key in db.dbType.keys():
            print "%s (%s back-end)"%(key,db.dbType[key])    
    else:
        print "No connection found."

def alias(self,arg):
    name,fstring = arg.split(" ",1)
    print "new alias: %s <%s>"%(dbprint.msgGREEN(name),fstring)
    __alias_table__[name]=fstring
    func,params = fstring.split(" ",1)
    def afunc(self,arg):
        print fstring
        ip.magic("%%%s"%fstring)
    ip.expose_magic(name,afunc)

def dbhelp(self,arg):
    cmdList = cmdDict.keys()
    cmdList.sort()
    sep = 0
    for i in cmdList:
        if sep<len(str(i)): sep=len(str(i))
    if  not arg:
        msg = "Available commands:\n"
        for cmd in cmdList:
            msg+="%s%s %s\n"%(dbprint.msgGREEN(cmd)," "*abs(sep-len(cmd)),cmdDict[cmd])
    else:
        cmd = arg.strip()
        if cmdDictExt.has_key(cmd):
           msg = "\n%s: %s\n"%(dbprint.msgGREEN(cmd),cmdDictExt[cmd])
        else:
           msg = dbprint.msgRED("\nSuch command is not available\n")
    print msg

def source(self,arg):
    if is_ready(): return
    f = None
    try:
        f = open(arg,'r')
    except:
        msg = "No such file '%s'"%arg
        raise msg
    qList = f.read().split(';')
    for q in qList:
        query = f.read().replace('\n',' ').replace(";","")
        print "\n+++EXECUTE:",query
        db.execute(dbAlias(),query)

def format(self,arg):
    if is_ready(): return
    if not (arg.lower()=="txt" or arg.lower()=="xml" or arg.lower()=="html" or arg.lower()=="csv"):
       raise dbprint.msgRED("ERROR: not supported format, please use txt,xml,html,csv")
    db.printMethod=arg
    
#
# Immitate SQL statements
#
def select(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'select')
    if is_ready(): return
    db.execute(dbAlias(),"select "+arg.replace(";",""))

def insert(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'insert')
    if is_ready(): return
    db.execute(dbAlias(),"insert "+arg.replace(";",""),listResults=0)

def drop(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'drop')
    if is_ready(): return
    params = arg.replace(";","").split()
    if params[0].lower()=="table":
       db.dropTable(dbAlias(),params[1])
    elif params[0].lower()=="database":
       db.dropDB(dbAlias())
    else:
       db.execute(dbAlias(),"drop "+arg.replace(";",""),listResults=0)
       db.reconnect(dbAlias(),reloadTables=1)
    msg = "'%s' executed successfully"%("drop "+arg,)
    print dbprint.msgGREEN(msg)

def update(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'update')
    if is_ready(): return
    db.execute(dbAlias(),"update "+arg.replace(";",""),listResults=0)

def create(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'create')
    if is_ready(): return
    db.execute(dbAlias(),"create "+arg.replace(";",""),listResults=0)
    db.reconnect(dbAlias())
    msg = "'%s' executed successfully"%("create "+arg,)
    print dbprint.msgGREEN(msg)

def alter(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'alter')
    if is_ready(): return
    db.execute(dbAlias(),"alter "+arg.replace(";",""),listResults=0)

def set(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'set')
    if is_ready(): return
    db.execute(dbAlias(),"set "+arg.replace(";",""),listResults=0)

def rollback(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'rollback')
    if is_ready(): return
    db.execute(dbAlias(),"rollback "+arg.replace(";",""),listResults=0)

def begin(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'begin')
    if is_ready(): return
    db.execute(dbAlias(),"begin "+arg.replace(";",""),listResults=0)

def commit(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'commit')
    if is_ready(): return
    db.execute(dbAlias(),"commit "+arg.replace(";",""),listResults=0)

def explain(self,arg):
    if arg and arg.lower()=='help': return dbhelp(self,'explain')
    if is_ready(): return
    db.execute(dbAlias(),"explain "+arg.replace(";",""))

#
# Main function
#
def main():
    o = ip.options
    ip.expose_magic('connect',connect)

    # SQL commands
    ip.expose_magic('select',select)
    ip.expose_magic('SELECT',select)
    ip.expose_magic('insert',insert)
    ip.expose_magic('INSERT',insert)
    ip.expose_magic('drop',drop)
    ip.expose_magic('DROP',drop)
    ip.expose_magic('update',update)
    ip.expose_magic('UPDATE',update)
    ip.expose_magic('create',create)
    ip.expose_magic('CREATE',create)
    ip.expose_magic('alter',alter)
    ip.expose_magic('ALTER',alter)
    ip.expose_magic('set',set)
    ip.expose_magic('SET',set)
    ip.expose_magic('rollback',rollback)
    ip.expose_magic('ROLLBACK',rollback)
    ip.expose_magic('begin',begin)
    ip.expose_magic('BEGIN',begin)
    ip.expose_magic('commit',commit)
    ip.expose_magic('COMMIT',commit)
    ip.expose_magic('explain',explain)
    ip.expose_magic('EXPLAIN',explain)

    ip.expose_magic('close',close)
    ip.expose_magic('rerun',rerun)
    ip.expose_magic('dbhelp',dbhelp)
    ip.expose_magic('show',show)
    ip.expose_magic('desc',desc)
    ip.expose_magic('dump',dump)
    ip.expose_magic('page',page)
    ip.expose_magic('next',next)
    ip.expose_magic('prev',prev)
    ip.expose_magic('migrate',migrate)
    ip.expose_magic('mydb',mydb)
    ip.expose_magic('alias',alias)
    ip.expose_magic('source',source)
    ip.expose_magic('format',format)
    # autocall to "full" mode (smart mode is default, I like full mode)
    o.autocall = 2
    
    # Jason Orendorff's path class is handy to have in user namespace
    # if you are doing shell-like stuff
    try:
        ip.ex("from path import path" )
    except ImportError:
        pass
    
    ip.ex('import os')
        
    # Set dbsh prompt
    o.prompt_in1= 'dbsh |\#> '
    o.prompt_in2= 'dbsh> '
    o.prompt_out= '<\#> '
    
    # define dbsh banner
    ver = "%s.%s"%(dbsh.__version__,dbsh.__revision__)
    pyver = sys.version.split('\n')[0]
    ipyver = Release.version
    msg = "Welcome to dbsh %s!\n[python %s, ipython %s]\n%s\n"%(ver,pyver,ipyver,os.uname()[3])
    msg+="For dbsh help use "+dbprint.msgBLUE("dbhelp")+", for python help use help commands\n"
    o.banner = msg
    o.prompts_pad_left="1"
    # Remove all blank lines in between prompts, like a normal shell.
    o.separate_in="0"
    o.separate_out="0"
    o.separate_out2="0"
    
main()
