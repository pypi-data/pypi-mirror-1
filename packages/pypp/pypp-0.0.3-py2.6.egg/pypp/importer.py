#!/usr/bin/env python
""" Module Importer class
    project: pypp
    
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "$Id: importer.py 14 2009-03-19 15:57:53Z jeanlou.dupont $"

__all__ = ['Importer']

import imp
import os
import sys
from types import *

class Importer(object):
    
    __slots__ = ['callback_import_module']
    
    def __init__(self):
        self.callback_import_module = None
    
    def find_module(self, fullname, path=None):
        """
        Case1:  X  where X is package thus X.__init__ is module
        Case2:  X  where X is module
        
        Case3:  X.Y where X is package & Y is package thus X.Y.__init__ is module
        Case4:  X.Y where X is package & Y is module
                
        We have to go through some hoops because imp.find_module
        does not handle the X.Y case directly. The package X must
        have been dealt with prior to calling imp.find_module;
        thus, when X.Y is encountered, we first make sure the package
        isn't loaded yet and then we process X.__init__ module
        (assuming it can be found in the filesystem).
        """
        #print "find_module: fullname(%s) path(%s)" % (fullname, path)
        origName = fullname
        
        lookupName = None
        
        # when we split at the last . 
        # we can't be sure we aren't dealing with a package
        # or a module just yet: we have to check if the resulting
        # path lands on a dir or a file.
        if '.' in fullname:
            pkg_name, name = fullname.rsplit('.', 1)
            
            #let's check if a package is already loaded
            mod = sys.modules.get(pkg_name, None)
            
            #if YES THEN we have a module to process.
            if type(mod) is ModuleType:
                path = mod.__path__ if hasattr(mod,'__path__') else path
                lookupName = name
            else:
            #we have to process X.__init__ then.
                lookupName = fullname
                
        else:
        # it's not because there isn't a . in the fullname
        # that we can be sure we are dealing with a package.
            lookupName = fullname

        #print "*looking for: lookup-name(%s) path(%s)" % (lookupName, path)
        
        try:
            file, rpath, desc = imp.find_module(lookupName, path)
        except:
            # we have nothing to do here: the interpreter has
            # given us a wrong path to look into
            return None
        
        _isdir  = os.path.isdir(rpath)
        _isfile = os.path.isfile(rpath)
        
        # readability...
        _ispkg = _isdir
        _ismod = _isfile
        
        if (_ispkg):
            return self._handlePkg(origName, rpath, file, desc)
        
        if (_ismod):
            return self._handleMod(origName, rpath, rpath, file, desc)
        
        return None
        
    def _handlePkg(self, name, rpath, file, desc):
        """ Handles package loading
        
            rpath: filesystem path to package where __init__ should be found
        """
        mod_path = os.path.join(rpath,'__init__.py')
        return self._handleMod(name, rpath, mod_path, file, desc)
    
    def _handleMod(self, name, rpath, path, file, desc):
        """ Handles module loading
        
            path: filesystem path to the module (i.e. mod-name.py)
        """
        frame = sys._getframe(1)
        global_scope = frame.f_globals
        
        return self.callback_import_module(name, rpath, path, file, desc, global_scope)
