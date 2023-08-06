#!/usr/bin/env python
""" Controller class
    project: pypp
    
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "$Id: controller.py 11 2009-03-05 06:05:39Z jeanlou.dupont $"

__all__ = ['Controller']

import os
import sys

from preprocessor import Tpl

class Controller(object):
    """
    """
    #__slots__ = ['_processed', '_loader']
    
    def __init__(self):
        
        #load class
        self._loader = None
        self._processed = {}
    
    def handle_import_module(self, name, rpath, path, file, desc, global_scope):
        """
        """
        #paranoia
        if (name in self._processed):
            return None
        
        self._processed[name] = path
        #print "handle_import_module: name(%s) rpath(%s)" % (name, rpath)
    
        #Perform the preprocessing
        if (file):
            processed_file = self.preprocessModule(name, file)
        else:
            processed_file = self.preprocessPackage(name, path)
    
        #Finally load
        try:
            return self._loader(name, processed_file, rpath, desc, global_scope)
        except ImportError:
            pass #pass-through
        
        return None

    def preprocessModule(self, name, file):
        """
        """
        #get rid of originating file because
        # we will anyway generate a new one
        path = file.name
        file.close()
        print "Controller.preprocessModule: name(%s)" % name
        return self._preprocessFile(name, path)
        

    def preprocessPackage(self, name, path):
        """
        """
        print "Controller.preprocessPackage: name(%s)" % name
        return self._preprocessFile(name, path)


    def _preprocessFile(self, name, path):
        """
        """

        #first, read source file in
        try:
            file = open(path)
            text = file.read()
        except:
            raise ImportError
        
        #next, determine if we have a directive .pypp
        # If we can't find one, we still have to return
        # a valid file object to the caller.
        if (text.find("#.pypp")==-1):
            return file
        
        print "pypp: found directive, name(%s)" % name
        
        # if an error occurs, let it trickle up
        # TODO is there a better to handle exceptions here??
        dir = os.path.dirname(path)
        rendered = Tpl(text, dirs=dir).render()

        processed_path = path + '.pypp'
        
        try:
            file = open( processed_path, "w")
            file.write(rendered)
        except Exception,e:
            raise RuntimeError("pypp: error writing rendered file, path(%s) exception(%s)" % (processed_path, e))
        finally:
            file.close()
            
        # lastly, re-open the file but this time in read-only mode
        try:
            file = open(processed_path)
        except Exception,e:
            raise RuntimeError("pypp: error opening rendered file, path(%s) exception(%s)" % (processed_path, e) )
        
        return file

    def _processed(self):
        """ for debugging purpose
        """
        for i in self._processed:
            yield i
        