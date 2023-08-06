#!/usr/bin/env python
""" Module Loader class
    project: pypp
    
    @author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__version__ = "$Id: loader.py 5 2009-03-02 18:16:37Z jeanlou.dupont $"

__all__ = ['Loader']

import os
import imp
import sys

class Loader(object):
    """ Loads a .pypp file in place of the usual .py
    """
    def __init__(self, name, file, path, desc, global_scope):
        self.name = name
        self.file = file
        self.path = path
        self.desc = desc
        self.global_scope = global_scope
    
    def load_module(self, fullname):
        isfile = self.file is not None
        
        #print "Loader.load_module: file(%s) fullname(%s) name(%s) path(%s)" % (isfile, fullname, self.name, self.path)
        
        try:
            mod = imp.load_module(self.name, self.file, self.path, self.desc)
        finally:
            if self.file:
                self.file.close()
        sys.modules[fullname] = mod
        
        return mod
    
