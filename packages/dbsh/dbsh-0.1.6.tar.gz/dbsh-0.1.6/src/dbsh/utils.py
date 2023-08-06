#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################
"""
Common utilities
"""
from dbsh import *

# Python Cookbook
def fetchsome(cursor, arraysize=10):
    """A generator that simplifies the use of fetchmany"""
    while True:
          results = cursor.fetchmany(arraysize)
          if not results: break
          for result in results:
              yield result
def fetchFromTo(cursor, iLimit=10, iOffset=0):
    """A way to retrieve a limited number of rows"""
#    if iOffset:
#       for i in xrange(0,iOffset):
#           cursor.next()
    results = cursor.fetchmany(iLimit)
    if not results: return
    for result in results:
        yield result

def swapDict(original_dict):
    return dict([(v, k) for (k, v) in original_dict.iteritems()])

def elementwise(fn):
    def newfn(arg):
        if hasattr(arg,'__getitem__'):  # is a Sequence
            return type(arg)(map(fn, arg))
        else:
            return fn(arg)
    return newfn

@elementwise
def itemLen(x):
    return len(str(x))

def makeTIME(intime):
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(long(intime)))

