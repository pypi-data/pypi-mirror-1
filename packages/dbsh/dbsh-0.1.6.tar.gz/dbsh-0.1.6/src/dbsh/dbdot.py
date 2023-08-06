#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
# This code belong to Andrew J. Dolgert <ajd27@cornell.edu> and used by him
# and Valentin Kuznetsov for other project.
#
class DotGraph(object):
    def __init__(self, file):
        self.name = "G"
        self.edges = []
        self.out = file
    
    def Name(self,name):
        self.name = name
        
    def AddEdge(self,start,finish):
        self.edges.append((start,finish))
        
    def Finish(self):
        print >>self.out, "digraph %s {" % (self.name)
        for edge in self.edges:
            print >>self.out, "    %s -> %s;" % (edge)
        print >>self.out, "}"

